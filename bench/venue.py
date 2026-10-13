"""Run the challenge, speed and document tests against any OpenAI-compatible server, timed by this client.

Usage: python3 bench/venue.py --base-url http://127.0.0.1:8000/v1 --model NAME --venue l40s-vllm --results FILE [options]
Works for vLLM (through an SSH tunnel), Ollama's /v1 endpoint, or any other OpenAI-compatible server. Run it on the
Mac so every venue gets byte-identical documents (they are cut from this machine's Python standard library).

Thinking off is model-specific, so pass it as extra request fields, for example:
  Qwen 3.8 on vLLM:   --extra '{"chat_template_kwargs": {"enable_thinking": false}}'
  Ollama /v1:         --extra '{"reasoning_effort": "none"}'
  OpenRouter:         --extra '{"reasoning": {"enabled": false}, "provider": {"only": ["deepinfra/fp8"], "allow_fallbacks": false}}'
Any reply that still contains reasoning is rejected by consume_stream, so a wrong setting fails instead of skewing results.

Hosted APIs need a key: --api-key-env OPENROUTER_API_KEY [--env-file .env]. --expect-provider DeepInfra rejects any
reply the service reports as served by someone else.
"""
import argparse
import datetime
import hashlib
import json
import os
import statistics
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from quiz import MAX_TOKENS, challenge_questions
from speed import REPLY_TOKENS, document_text, same_text_chars

GEN_PROMPT = "Explain in about 200 words how a refrigerator keeps food cold."
TIMING = ("Client wall time, including the network between this Mac and the server. First text is the first nonempty "
          "visible text chunk. Throughput is completion tokens / total request seconds.")


def load_key(name, env_file=None):
    """Read only the named variable, from the environment or a dotenv file. Never source shell code or print it."""
    key = os.environ.get(name, "").strip()
    if not key and env_file:
        for line in Path(env_file).expanduser().read_text().splitlines():
            var, sep, value = line.strip().removeprefix("export ").partition("=")
            if sep and var.strip() == name:
                key = value.strip().strip("\"'")
    if not key:
        raise ValueError(f"Set {name} or pass --env-file with that variable.")
    if any(c.isspace() for c in key) or key.startswith(("$", "{{")):
        raise ValueError(f"{name} must be a literal value, not a shell or secret reference.")
    return key


def consume_stream(lines, started, clock=time.perf_counter):
    """Measure visible text chunks, not SSE packets (a packet can contain multiple tokens)."""
    text, reasoning, chunks = [], [], []
    first = last = None
    usage, meta, finish, done = {}, {}, None, False
    for raw in lines:
        line = raw.decode("utf-8").strip() if isinstance(raw, bytes) else raw.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            done = True
            break
        event = json.loads(data)
        if event.get("error"):
            raise RuntimeError("The server returned a stream error; run is incomplete.")
        for k in ("id", "model", "provider", "system_fingerprint"):
            if event.get(k) is not None:
                meta[k] = event[k]
        if event.get("usage"):
            usage = event["usage"]
        for choice in event.get("choices", []):
            delta = choice.get("delta") or {}
            if delta.get("content"):
                now = clock()
                first = now if first is None else first
                last = now
                text.append(delta["content"])
                chunks.append({"elapsed_s": now - started, "text": delta["content"]})
            if delta.get("reasoning"):
                reasoning.append(delta["reasoning"])
            if delta.get("reasoning_details"):
                reasoning.append(json.dumps(delta["reasoning_details"]))
            finish = choice.get("finish_reason") or finish
    elapsed = clock() - started
    if not done or finish not in ("stop", "length") or first is None:
        raise RuntimeError("Incomplete or non-text completion; no score recorded.")
    if not isinstance(usage.get("completion_tokens"), int):
        raise RuntimeError("Missing token usage; no throughput recorded.")
    if reasoning or (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0):
        raise RuntimeError("Server returned reasoning despite thinking-off; run is not comparable.")
    return {"response": "".join(text), "seconds": elapsed,
            "time_to_first_text_s": first - started, "last_text_s": last - started,
            "completion_tokens_per_total_second": usage["completion_tokens"] / elapsed,
            "usage": usage, "finish_reason": finish, "metadata": meta, "chunks": chunks}


def payload(model, prompt, max_tokens, seed=0, extra=None):
    return {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "seed": seed,
            "max_tokens": max_tokens, "stream": True, "stream_options": {"include_usage": True}, **(extra or {})}


def complete(base_url, request, key=None, provider=None, timeout=4 * 3600):  # Qwen 3.8 27B waits about 1.8 hours at 262K on the Mac
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(base_url + "/chat/completions", data=json.dumps(request).encode(), headers=headers)
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = consume_stream(response, started)
    if provider and result["metadata"].get("provider") != provider:
        raise RuntimeError(f"Served by {result['metadata'].get('provider')!r}, not {provider!r}; result rejected.")
    return result


def grade(row, grader):
    """A reply cut off at the token cap counts as wrong, as in quiz.py."""
    limited = row["finish_reason"] == "length"
    correct, detail = (False, "output token limit") if limited else grader(row["response"])
    row.update(correct=bool(correct and not limited), detail=detail, hit_token_limit=limited)
    return row


def read_document(base_url, model, ctx, extra=None, key=None, provider=None):
    """One document of the deck's same-text size for ctx, with a unique first line so nothing is cached."""
    text = document_text(same_text_chars(ctx))
    prompt = f"[run {uuid.uuid4()}]\n{text}\n\nExplain what the code above does in about 150 words."
    try:
        r = complete(base_url, payload(model, prompt, REPLY_TOKENS, extra=extra), key, provider)
    except urllib.error.HTTPError as e:
        message = e.read().decode(errors='replace')
        context_error = e.code == 400 and any(term in message.lower() for term in
            ("maximum context length", "max_model_len", "context window", "context_length_exceeded"))
        if not context_error:
            raise RuntimeError(f"Document request failed with HTTP {e.code}; not a context-limit result.") from None
        return {"context": ctx, "document_chars": len(text), "too_long": True,
                "error": f"HTTP {e.code}: {message[:300]}"}
    tokens = r["usage"]["prompt_tokens"]
    return {"context": ctx, "document_chars": len(text), "prompt_tokens": tokens,
            "wait_before_first_text_s": round(r["time_to_first_text_s"], 2),
            "reading_tok_s": round(tokens / r["time_to_first_text_s"], 1),
            "reply_tokens": r["usage"]["completion_tokens"], "seconds": round(r["seconds"], 2), "cost": r["usage"].get("cost")}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + "\n")
    temp.replace(path)


def summarize(data):
    rows, runs = data["questions"], data["speed_runs"]
    out = {}
    if rows:
        out.update(correct=sum(r["correct"] for r in rows), total=len(rows),
                   overall_pct=100 * sum(r["correct"] for r in rows) / len(rows),
                   avg_seconds_per_question=statistics.mean(r["seconds"] for r in rows),
                   hit_token_limit=sum(r["hit_token_limit"] for r in rows))
    if runs:
        out.update(median_time_to_first_text_s=statistics.median(r["time_to_first_text_s"] for r in runs),
                   median_completion_tokens_per_total_second=statistics.median(r["completion_tokens_per_total_second"] for r in runs))
    # Hosted APIs report a cost per request; local servers do not, so the total appears only when every request has one.
    costs = [r["usage"].get("cost") for r in [data.get("smoke", {"usage": {}}), *rows, *runs]]
    costs += [d.get("cost") for d in data.get("documents", []) if not d.get("too_long")]
    if all(isinstance(c, (int, float)) for c in costs):
        out["reported_cost_usd"] = sum(costs)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", required=True, help="the server's OpenAI-compatible root, ending in /v1")
    ap.add_argument("--model", required=True, help="model name as the server knows it")
    ap.add_argument("--venue", required=True, help="short label for where it ran, e.g. l40s-vllm")
    ap.add_argument("--baseline", help="the Mac's Ollama tag for the same model, for comparison")
    ap.add_argument("--precision", help="weight format on this venue, e.g. fp8")
    ap.add_argument("--server", help="server software and version, e.g. 'vLLM 0.x.y'")
    ap.add_argument("--extra", type=json.loads, default={}, help="extra request fields as JSON, e.g. thinking off")
    ap.add_argument("--mode", choices=["smoke", "speed", "challenge", "documents", "all"], default="all")
    ap.add_argument("--contexts", default="2048,8192,32768,131072,262144")
    ap.add_argument("--api-key-env", help="environment variable holding an API key, e.g. OPENROUTER_API_KEY")
    ap.add_argument("--env-file", type=Path, help="dotenv file to read that variable from")
    ap.add_argument("--expect-provider", help="reject replies the service says another provider served, e.g. DeepInfra")
    ap.add_argument("--results", type=Path, required=True)
    args = ap.parse_args()
    key = load_key(args.api_key_env, args.env_file) if args.api_key_env else None
    send = lambda request: complete(args.base_url, request, key, args.expect_provider)
    if args.results.exists():
        raise SystemExit("Results file already exists. Choose a new --results path to keep earlier evidence.")
    questions = list(challenge_questions())
    data = {"schema_version": 1, "venue": args.venue, "server": args.server, "base_url": args.base_url,
            "measured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "model": args.model,
            "local_baseline_tag": args.baseline, "precision": args.precision, "expect_provider": args.expect_provider,
            "settings": {"set": "challenge", "temperature": 0, "seed": 0, "think": False, "max_tokens": MAX_TOKENS,
                         "extra": args.extra,
                         "prompt_sha256": hashlib.sha256(json.dumps([p for _, p, _ in questions]).encode()).hexdigest()},
            "timing": TIMING, "status": "running", "questions": [], "speed_runs": [], "documents": []}
    save(args.results, data)
    try:
        data["smoke"] = send(payload(args.model, "Reply with exactly OK.", 16, extra=args.extra))
        data["smoke"].pop("chunks")
        if data["smoke"]["response"].strip().rstrip(".") != "OK":
            raise RuntimeError(f"Smoke response was {data['smoke']['response'][:80]!r}, not OK.")
        save(args.results, data)
        print(f"{args.venue} {args.model}: smoke OK", flush=True)
        if args.mode in ("speed", "all"):
            for seed in range(3):
                row = send(payload(args.model, GEN_PROMPT, 300, seed, args.extra))
                row.pop("chunks")
                data["speed_runs"].append(row)
                save(args.results, data)
            print(f"  speed: {summarize(data)}", flush=True)
        if args.mode in ("challenge", "all"):
            for n, (category, prompt, grader) in enumerate(questions, 1):
                row = send(payload(args.model, prompt, MAX_TOKENS, extra=args.extra))
                row.pop("chunks")
                row.update(n=n, category=category)
                data["questions"].append(grade(row, grader))
                save(args.results, data)
                print(f"  Q{n} {category}: {'OK' if row['correct'] else 'BAD'} ({row['seconds']:.1f}s)", flush=True)
        if args.mode in ("documents", "all"):
            for ctx in (int(c) for c in args.contexts.split(",") if c):  # --contexts "" skips documents
                doc = read_document(args.base_url, args.model, ctx, args.extra, key, args.expect_provider)
                data["documents"].append(doc)
                save(args.results, data)
                print(f"  document {ctx}: {doc}", flush=True)
        data["summary"], data["status"] = summarize(data), "complete"
    except (Exception, KeyboardInterrupt) as e:
        data["status"], data["error"] = "incomplete", f"{type(e).__name__}: {e}"
        raise
    finally:
        save(args.results, data)
    print(f"{args.venue} {args.model}: {data['summary']}", flush=True)


if __name__ == "__main__":
    main()

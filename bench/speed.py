"""Measure load time, generation speed, prompt-reading speed and memory for local Ollama models.

Usage: python3 bench/speed.py [--contexts 2048,32768] [--documents-only] [--same-text] [--results FILE] [model ...]
Writes bench/results/speed.json, or FILE (merged per model, so runs can be split across invocations).
"""
import argparse
import datetime
import json
import pathlib
import platform
import statistics
import subprocess
import sysconfig
import urllib.error
import uuid

from ollama_client import NS, PeakMemory, chat, get, has_baked_system_prompt, installed_models, runner_memory_gb, unload_all

RESULTS = pathlib.Path(__file__).parent / "results" / "speed.json"
GEN_PROMPT = "Explain in about 200 words how a refrigerator keeps food cold."
GEN_TOKENS = 300
RUNS = 3
REPLY_TOKENS = 200
# --same-text sends every model the same characters per document size: enough to fill FILL of the context at
# CHARS_PER_TOKEN_FLOOR, which is denser than any tokenizer measured on this text (Gemma 4 is about 3.4).
CHARS_PER_TOKEN_FLOOR = 3.2
FILL = 0.9


def same_text_chars(ctx):
    return int(ctx * FILL * CHARS_PER_TOKEN_FLOOR)


def document_text(chars):
    """Real-world filler text: Python standard library source, concatenated."""
    lib = pathlib.Path(sysconfig.get_paths()["stdlib"])
    out, total = [], 0
    for f in sorted(lib.glob("*.py")):
        t = f.read_text(errors="ignore")
        out.append(t)
        total += len(t)
        if total >= chars:
            break
    return "".join(out)[:chars]


def read_document(model, text, num_ctx):
    """Send a document (with a unique prefix to defeat prompt caching) and ask for a one-line summary."""
    prompt = f"[run {uuid.uuid4()}]\n{text}\n\nExplain what the code above does in about 150 words."
    r = chat(model, prompt, num_predict=REPLY_TOKENS, num_ctx=num_ctx)
    return {
        "document_chars": len(text),
        "prompt_tokens": r["prompt_eval_count"],
        # Ollama silently drops the start of a prompt that does not fit, so flag any document that may have been cut.
        "truncated": r["prompt_eval_count"] + REPLY_TOKENS >= num_ctx,
        "prefill_tok_s": round(r["prompt_eval_count"] / (r["prompt_eval_duration"] / NS), 1),
        "wait_before_first_token_s": round(r["prompt_eval_duration"] / NS, 2),
        "reply_tokens": r["eval_count"],
        "gen_tok_s_with_document": round(r["eval_count"] / (r["eval_duration"] / NS), 1) if r["eval_count"] >= 50 else None,
        "memory_gb_after": runner_memory_gb(model),
    }


def bench_model(model, contexts, generation=True, same_text=False):
    unload_all()
    result = {"ollama_version": get("/api/version")["version"]}
    if generation:
        cold = chat(model, "Hi", num_predict=1, num_ctx=4096)
        result |= {"load_seconds": round(cold["load_duration"] / NS, 1), "memory_gb_idle": runner_memory_gb(model)}
        gens = []
        for seed in range(RUNS):
            r = chat(model, GEN_PROMPT, num_predict=GEN_TOKENS, num_ctx=4096, seed=seed)
            gens.append(r["eval_count"] / (r["eval_duration"] / NS))
        result["gen_tok_s"] = round(statistics.median(gens), 1)
        result["gen_tok_s_runs"] = [round(g, 1) for g in gens]

    # Calibrate characters-per-token so documents land close to each target context.
    chars_per_token = None
    if not same_text:
        try:
            probe = read_document(model, document_text(6000), 8192)
            chars_per_token = 6000 / probe["prompt_tokens"]
        except urllib.error.HTTPError:
            chars_per_token = 3.3  # typical for Python source with these tokenizers
            unload_all()

    result["contexts"] = {}
    for ctx in contexts:
        text = document_text(same_text_chars(ctx) if same_text else int((ctx - REPLY_TOKENS) * chars_per_token * 0.97))
        try:
            # Fresh runner loaded at this context size, so memory left over from earlier documents is not counted.
            unload_all()
            chat(model, "Hi", num_predict=1, num_ctx=ctx)
            with PeakMemory(model) as peak:
                runs = [read_document(model, text, ctx) for _ in range(RUNS if ctx <= 8192 else 1)]
        except urllib.error.HTTPError:
            result["contexts"][str(ctx)] = {"crashed": True, "memory_gb": None}
            print(f"  {model} ctx={ctx}: CRASHED (Ollama runner)", flush=True)
            unload_all()
            continue
        best = runs[-1]
        best["memory_gb"] = peak.gb
        best["prefill_tok_s"] = round(statistics.median(r["prefill_tok_s"] for r in runs), 1)
        best["wait_before_first_token_s"] = round(statistics.median(r["wait_before_first_token_s"] for r in runs), 2)
        result["contexts"][str(ctx)] = best
        print(f"  {model} ctx={ctx}: {best}", flush=True)
    unload_all()
    return result


def environment():
    hw = subprocess.run(["system_profiler", "SPHardwareDataType"], capture_output=True, text=True).stdout
    pick = lambda key: next((l.split(":", 1)[1].strip() for l in hw.splitlines() if key in l), None)
    return {
        "measured_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "macos": platform.mac_ver()[0],
        "model_identifier": pick("Model Identifier"),
        "chip": pick("Chip"),
        "memory": pick("Memory"),
        "power": subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True).stdout.splitlines()[0],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", default="2048,8192,32768")
    ap.add_argument("--documents-only", action="store_true", help="skip load time and generation speed")
    ap.add_argument("--same-text", action="store_true", help="send every model the same characters per document size")
    ap.add_argument("--results", type=pathlib.Path, default=RESULTS)
    ap.add_argument("models", nargs="*")
    args = ap.parse_args()
    contexts = [int(c) for c in args.contexts.split(",")]
    out = args.results
    data = json.loads(out.read_text()) if out.exists() else {"models": {}}
    data["environment"] = environment()
    for model in args.models or installed_models():
        print(f"== {model}", flush=True)
        prev = data["models"].get(model, {})
        new = bench_model(model, contexts, generation=not args.documents_only, same_text=args.same_text)
        new["system_prompt_replaced"] = has_baked_system_prompt(model)
        new["contexts"] = {**prev.get("contexts", {}), **new["contexts"]}
        data["models"][model] = {**prev, **new}
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()

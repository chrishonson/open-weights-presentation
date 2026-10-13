"""Time the Mac the way the OpenRouter runs were timed: the same streamed requests, measured by the client.

Usage: OLLAMA_HOST=127.0.0.1:11436 python3 bench/mac_client_speed.py [--results FILE]
Sends the OpenRouter speed requests (same prompt, 300-token cap, seeds 0 to 2, temperature 0, thinking off) to
Ollama's OpenAI-compatible endpoint, after one untimed request that loads the model.
"""
import argparse
import datetime
import json
import os
import statistics
import time
import urllib.request
from pathlib import Path

from venue import GEN_PROMPT, consume_stream, save

HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434").rstrip('/')
HOST = HOST if '://' in HOST else 'http://' + HOST
RESULTS = Path(__file__).parent / "results" / "mac-client-speed.json"
TAGS = ("gemma4:26b-nvfp4", "qwen3.8:27b")  # the Mac builds of the two models run on OpenRouter


def payload(tag, prompt, max_tokens, seed=0):
    return {"model": tag, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "seed": seed,
            "max_tokens": max_tokens, "reasoning_effort": "none", "stream": True, "stream_options": {"include_usage": True}}


def complete(request):
    req = urllib.request.Request(HOST + "/v1/chat/completions", data=json.dumps(request).encode(),
                                 headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=600) as response:
        return consume_stream(response, started)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, default=RESULTS)
    args = ap.parse_args()
    if args.results.exists():
        raise SystemExit("Results file already exists. Choose a new --results path to keep earlier evidence.")
    version = json.load(urllib.request.urlopen(HOST + "/api/version"))["version"]
    out = {"measured_at": datetime.datetime.now().isoformat(timespec="seconds"), "ollama_version": version,
           "status": "incomplete", "models": {}}
    save(args.results, out)
    for tag in TAGS:
        complete(payload(tag, "Reply with exactly OK.", 16))  # load the model, untimed
        runs = [complete(payload(tag, GEN_PROMPT, 300, seed)) for seed in range(3)]
        for r in runs:
            r.pop("chunks")
        out["models"][tag] = {"speed_runs": runs, "summary": {
            "median_time_to_first_text_s": statistics.median(r["time_to_first_text_s"] for r in runs),
            "median_completion_tokens_per_total_second": statistics.median(r["completion_tokens_per_total_second"] for r in runs)}}
        print(tag, out["models"][tag]["summary"], flush=True)
        save(args.results, out)
    out['status'] = 'complete'
    save(args.results, out)


if __name__ == "__main__":
    main()

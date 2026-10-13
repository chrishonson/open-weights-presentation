"""Publish the three-environment table (Mac, L40S, OpenRouter) into index.html; no network calls.

Every number comes from runs timed by the same client on the Mac (bench/venue.py, and its predecessor bench/openrouter.py for the OpenRouter questions):
bench/results/mac-venue-*.json, l40s-*.json and openrouter-*.json. Missing results distinguish failed attempts from untested cases.
"""
import json
from pathlib import Path

from publish_openrouter import replace_section
from summarize import num, wait

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "bench" / "results"
MODELS = [("Qwen 3.8 27B", "qwen38-27b", "qwen38-27b"), ("Gemma 4 26B", "gemma4-26b", "gemma4-26b"),
          ("Nemotron 3.5 Lightning", "nemotron-3.5-lightning", None), ("Qwen 3.8 27B redteam", "qwen38-27b-redteam", None),
          ("Claude Haiku 5.5", "haiku55", "haiku55")]


def load(name):
    p = R / name
    return json.loads(p.read_text()) if p.exists() else None


def documents(*runs):
    """Documents by context size from the first run that has them."""
    return next(({d["context"]: d for d in r["documents"]} for r in runs if r and r.get("documents")), {})


# A Mac document size the shared-client run could not finish (macOS stopped long GPU reads while the Mac was in use)
# falls back to the Oct 22 measurement through Ollama's native API, marked with NATIVE. Document waits are server
# reading time, which matched across the two paths to within 6% where both exist.
NATIVE = "*"
NATIVE_NOTE = ("* Oct 22, through Ollama's native API. Later runs through the shared client were stopped by macOS "
               "while the Mac was in use.")


def native_wait(tag, ctx):
    data = json.loads((ROOT / "benchmarks.json").read_text())
    m = next((m for m in data["models"] if m["tag"] == tag), None)
    return (m or {}).get("by_context", {}).get(str(ctx), {}).get("wait_before_first_token_s")


def doc_cell(docs, ctx, run=None, native_tag=None):
    d = docs.get(ctx)
    if not d:
        fallback = native_tag and run and run.get("status") == "incomplete" and native_wait(native_tag, ctx)
        if fallback:
            return wait(fallback) + NATIVE
        return "failed" if run and run.get("status") == "incomplete" else "not tested"
    return "too long" if d.get("too_long") else wait(d["wait_before_first_text_s"])


def rows():
    out = []
    for name, slug, api in MODELS:
        mac = (load(f"mac-venue-{slug}-qa.json"), load(f"mac-venue-{slug}-docs.json"))
        gpu = (load(f"l40s-{slug}.json") or load(f"l40s-{slug}-qa.json"), load(f"l40s-{slug}-docs.json") or load(f"l40s-{slug}.json"))
        host = (load(f"openrouter-{api}.json") if api else None,
                load(f"openrouter-{api}-docs.json") or load(f"openrouter-{api}.json") if api else None)
        for where, (qa, docs_run) in (("This Mac", mac), ("Rented L40S", gpu), ("OpenRouter", host)):
            if not qa:
                continue
            assert qa["status"] == "complete" and len(qa["questions"]) == 29 and len(qa["speed_runs"]) == 3
            s = qa["summary"]
            assert sum(q["correct"] for q in qa["questions"]) == s["correct"]
            weights = qa.get("precision") or qa.get("endpoint", {}).get("quantization")
            weights = "API" if weights == "unknown" else (weights.upper() if weights in ("fp8", "bf16") else weights)
            docs = documents(docs_run)
            native = qa.get("local_baseline_tag") if where == "This Mac" else None
            out.append({"model": name, "where": where, "weights": weights, "score": f"{s['correct']}/{s.get('total', 29)}",
                        "per_answer": wait(s["avg_seconds_per_question"]),
                        "first_text": f"{num(s['median_time_to_first_text_s'], 2)} s",
                        "writing": num(s["median_completion_tokens_per_total_second"], 0),
                        "wait_131k": doc_cell(docs, 131072, docs_run, native),
                        "wait_262k": doc_cell(docs, 262144, docs_run, native)})
    return out


def html(table):
    cells = ("where", "weights", "score", "per_answer", "first_text", "writing", "wait_131k", "wait_262k")
    lines, previous = [], None
    for r in table:
        model = f'<td class="model-name">{r["model"]}</td>' if r["model"] != previous else "<td></td>"
        cls = ' class="first"' if r["model"] != previous else ""
        previous = r["model"]
        right = ' class="r num"'
        tds = "".join(f"<td{'' if c in ('where', 'weights') else right}>{r[c]}</td>" for c in cells)
        lines.append(f"<tr{cls}>{model}{tds}</tr>")
    return "\n".join(lines)


def comparison(table, kind):
    lines = []
    for name, *_ in MODELS:
        by = {r["where"]: r for r in table if r["model"] == name}
        if kind == "answers":
            cells = [f"<b>{by[w]['score']}</b> · {by[w]['per_answer']}" if w in by else "not tested"
                     for w in ("This Mac", "Rented L40S", "OpenRouter")]
        else:
            cells = [by.get(w, {}).get(c, "not tested")
                     for c in ("wait_131k", "wait_262k")
                     for w in ("This Mac", "Rented L40S", "OpenRouter")]
        lines.append("<tr><th>" + name + "</th>" + "".join("<td>" + c + "</td>" for c in cells) + "</tr>")
    return "\n".join(lines)


def main():
    table = rows()
    p = ROOT / "index.html"
    text = replace_section(p.read_text(), "environment-rows", html(table))
    for kind in ("answers", "documents"):
        text = replace_section(text, kind + "-rows", comparison(table, kind))
    p.write_text(text)


if __name__ == "__main__":
    main()

"""Run the 80-question quiz, or the challenge set, against local Ollama models and grade it automatically.

Usage: python3 bench/quiz.py [--think] [--set main|challenge] [--results FILE] [model ...]
Writes bench/results/quiz[-think].json (main) or challenge.json, with per-question results and per-model summaries.
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import tempfile
import textwrap
import urllib.error

from quiz_questions import (CHALLENGE_CODING, CHALLENGE_KEEP, CHALLENGE_MATH, CHALLENGE_MULTIPLE_CHOICE, CODING, HARD_CODING,
                            HARD_MATH, HARD_MULTIPLE_CHOICE, MATH, MULTIPLE_CHOICE)

RESULTS_DIR = pathlib.Path(__file__).parent / "results"
MAX_TOKENS = 6144

MATH_PROMPT = "Solve this problem.\n\n{q}\n\nEnd your reply with a final line in exactly this form: ANSWER: <number> (just the number, no units or $ sign)."
MC_PROMPT = "{q}\n\n{options}\n\nEnd your reply with a final line in exactly this form: ANSWER: <letter>"
CODE_PROMPT = "Write a Python function {spec}\n\nReply with a single ```python code block containing the complete function and any imports it needs. Do not include tests or example usage."


def final_answer(text):
    found = re.findall(r"ANSWER:\s*\**\s*([^\n*]+)", text, flags=re.I)
    return found[-1].strip() if found else None


def grade_math(text, expected):
    ans = final_answer(text)
    if ans is None:
        return False, None
    num = re.search(r"-?\d[\d,]*\.?\d*", ans)
    if not num:
        return False, ans
    return abs(float(num.group().replace(",", "")) - expected) < 0.01, ans


def grade_mc(text, expected):
    ans = final_answer(text)
    letter = re.match(r"\(?([A-D])\b", ans or "")
    return bool(letter) and letter.group(1) == expected, ans


def grade_code(text, task):
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.S)
    # Prefer the last block that defines the requested name; models often add example-output blocks after it.
    defining = [blk for blk in blocks if re.search(rf"^\s*(def|class)\s+{task['name']}\b", blk, flags=re.M)]
    code = textwrap.dedent((defining or blocks or [text])[-1])
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "solution.py"
        path.write_text(code + "\n\n" + task["tests"] + "\n")
        try:
            run = subprocess.run(["python3", "-I", str(path)], cwd=tmp, capture_output=True, text=True, timeout=10)
            return run.returncode == 0, run.stderr.strip().splitlines()[-1] if run.returncode else "pass"
        except subprocess.TimeoutExpired:
            return False, "timeout"


def questions():
    for q, a in MATH:
        yield "math", MATH_PROMPT.format(q=q), lambda t, a=a: grade_math(t, a)
    for q, opts, a in MULTIPLE_CHOICE:
        options = "\n".join(f"{l}) {o}" for l, o in zip("ABCD", opts))
        yield "knowledge", MC_PROMPT.format(q=q, options=options), lambda t, a=a: grade_mc(t, a)
    for task in CODING:
        yield "coding", CODE_PROMPT.format(spec=task["spec"]), lambda t, task=task: grade_code(t, task)
    for q, a in HARD_MATH:
        yield "hard", MATH_PROMPT.format(q=q), lambda t, a=a: grade_math(t, a)
    for q, opts, a in HARD_MULTIPLE_CHOICE:
        options = "\n".join(f"{l}) {o}" for l, o in zip("ABCD", opts))
        yield "hard", MC_PROMPT.format(q=q, options=options), lambda t, a=a: grade_mc(t, a)
    for task in HARD_CODING:
        yield "hard", CODE_PROMPT.format(spec=task["spec"]), lambda t, task=task: grade_code(t, task)


def challenge_questions():
    """Questions that separate models: kept ones from the main quiz (by number), then new ones. Categories are
    math, logic and coding."""
    main = list(questions())
    for n in CHALLENGE_KEEP:
        _, prompt, grader = main[n - 1]
        category = "math" if n <= 20 or 61 <= n <= 70 else "logic" if n <= 40 or 71 <= n <= 75 else "coding"
        yield category, prompt, grader
    for q, a in CHALLENGE_MATH:
        yield "math", MATH_PROMPT.format(q=q), lambda t, a=a: grade_math(t, a)
    for q, opts, a in CHALLENGE_MULTIPLE_CHOICE:
        options = "\n".join(f"{l}) {o}" for l, o in zip("ABCD", opts))
        yield "logic", MC_PROMPT.format(q=q, options=options), lambda t, a=a: grade_mc(t, a)
    for task in CHALLENGE_CODING:
        yield "coding", CODE_PROMPT.format(spec=task["spec"]), lambda t, task=task: grade_code(t, task)


QUESTION_SETS = {"main": questions, "challenge": challenge_questions}


def summarize(rows):
    pct = lambda sub: round(100 * sum(r["correct"] for r in sub) / len(sub), 1) if sub else None
    summary = {"overall_pct": pct(rows), "everyday_pct": pct([r for r in rows if r["category"] != "hard"])}
    for cat in ("math", "knowledge", "logic", "coding", "hard"):
        summary[f"{cat}_pct"] = pct([r for r in rows if r["category"] == cat])
    answered = [r for r in rows if not r.get("crashed")]
    summary["avg_seconds_per_question"] = round(sum(r["seconds"] for r in answered) / max(1, len(answered)), 1)
    summary["total_minutes"] = round(sum(r["seconds"] for r in rows) / 60, 1)
    summary["thought_before_answering"] = any(r["thinking_chars"] for r in rows)
    summary["hit_token_limit"] = sum(r["hit_token_limit"] for r in rows)
    summary["crashed"] = sum(r.get("crashed", False) for r in rows)
    return summary


def run_model(model, think, only=None, previous=None, question_set="main"):
    """Ask every question (or only one category, merged into previous rows) and grade the replies."""
    from ollama_client import NS, chat, unload_all
    unload_all()
    chat(model, "Hi", num_predict=1, num_ctx=8192)  # load once so load time is not billed to question 1
    rows = {r["n"]: r for r in (previous or [])}
    for i, (category, prompt, grader) in enumerate(QUESTION_SETS[question_set]()):
        if only and category != only:
            continue
        try:
            r = chat(model, prompt, num_predict=MAX_TOKENS, num_ctx=8192, think=think)
        except urllib.error.HTTPError:
            # Ollama's runner crashed three times on this question. Count it as wrong and keep going.
            rows[i + 1] = {"n": i + 1, "category": category, "correct": False, "detail": "Ollama runner crashed",
                           "seconds": 0, "tokens": 0, "thinking_chars": 0, "hit_token_limit": False, "crashed": True, "response": ""}
            print(f"  {model} #{i + 1} {category}: CRASH", flush=True)
            continue
        text = r["message"]["content"]
        ok, detail = grader(text)
        rows[i + 1] = {
            "n": i + 1,
            "category": category,
            "correct": ok,
            "detail": detail,
            "seconds": round(r["total_duration"] / NS, 2),
            "tokens": r["eval_count"],
            "thinking_chars": len(r["message"].get("thinking") or ""),
            "hit_token_limit": r["eval_count"] >= MAX_TOKENS,
            "response": text,
        }
        print(f"  {model} #{i + 1} {category}: {'OK ' if ok else 'BAD'} {detail!r:.60} {rows[i + 1]['seconds']}s", flush=True)
    unload_all()
    rows = [rows[n] for n in sorted(rows)]
    return {"summary": summarize(rows), "questions": rows}


def regrade(data):
    """Re-apply the graders to saved replies without asking the models again."""
    graders = [g for _, _, g in QUESTION_SETS[data.get("settings", {}).get("set", "main")]()]
    for model, entry in data["models"].items():
        for r in entry["questions"]:
            if "response" in r and not r.get("crashed"):
                r["correct"], r["detail"] = graders[r["n"] - 1](r["response"])
        entry["summary"] = summarize(entry["questions"])
        print(f"  {model}: {entry['summary']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--think", action="store_true", help="let models reason before answering (slower)")
    ap.add_argument("--category", choices=["math", "knowledge", "logic", "coding", "hard"], help="re-run one category and merge into saved results")
    ap.add_argument("--set", choices=sorted(QUESTION_SETS), default="main", help="main 80-question quiz, or the challenge set")
    ap.add_argument("--regrade", action="store_true", help="re-grade saved replies only")
    ap.add_argument("--results", type=pathlib.Path, help="results file (default: results/quiz.json or quiz-think.json)")
    ap.add_argument("models", nargs="*")
    args = ap.parse_args()
    default = "challenge" if args.set == "challenge" else "quiz"
    out = args.results or RESULTS_DIR / (f"{default}-think.json" if args.think else f"{default}.json")
    data = json.loads(out.read_text()) if out.exists() else {"models": {}}
    if args.regrade:
        regrade(data)
        out.write_text(json.dumps(data, indent=2))
        return
    from ollama_client import get, has_baked_system_prompt, installed_models
    data["settings"] = {"think": args.think, "temperature": 0, "max_tokens": MAX_TOKENS, "set": args.set}
    for model in args.models or installed_models():
        print(f"== {model}", flush=True)
        previous = data["models"].get(model, {}).get("questions") if args.category else None
        data["models"][model] = run_model(model, args.think, args.category, previous, args.set)
        data["models"][model]["measured_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        data["models"][model]["ollama_version"] = get("/api/version")["version"]
        data["models"][model]["system_prompt_replaced"] = has_baked_system_prompt(model)
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(data, indent=2))
        print(f"  {model}: {data['models'][model]['summary']}", flush=True)


if __name__ == "__main__":
    main()

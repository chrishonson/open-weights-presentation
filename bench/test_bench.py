"""Tests for the graders and summary helpers. They need no Ollama server. Run: python3 -m pytest bench"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the bench scripts import each other as top-level modules

from bench import quiz, summarize
from bench.quiz_questions import CODING, HARD_CODING, HARD_MATH, MATH, MULTIPLE_CHOICE


def test_answer_key_and_reference_solutions():
    assert len(MATH) == len(MULTIPLE_CHOICE) == len(CODING) == 20
    assert len(HARD_MATH) == 10 and len(HARD_CODING) == 5
    for task in CODING + HARD_CODING:
        exec(task["ref"] + "\n" + task["tests"], {})


def test_grade_math_accepts_formatting_and_rejects_wrong_or_missing():
    assert quiz.grade_math("work...\n**ANSWER: $30.50**", 30.5)[0]
    assert quiz.grade_math("ANSWER: 5,624.32", 5624.32)[0]
    assert not quiz.grade_math("ANSWER: 31", 30.5)[0]
    assert quiz.grade_math("no final line", 1) == (False, None)


def test_grade_mc_uses_last_answer_line():
    assert quiz.grade_mc("ANSWER: (D) None of these", "D")[0]
    assert quiz.grade_mc("**ANSWER:** C", "C")[0]
    assert not quiz.grade_mc("ANSWER: A\nActually, ANSWER: B", "A")[0]


def test_grade_code_runs_tests_and_prefers_the_defining_block():
    task = CODING[0]
    good = f"```python\n{task['ref']}\n```\nExample output:\n```python\nTrue\n```"
    assert quiz.grade_code(good, task) == (True, "pass")
    indented = "1. Here:\n   ```python\n" + "\n".join("   " + l for l in task["ref"].splitlines()) + "\n   ```"
    assert quiz.grade_code(indented, task)[0]
    assert quiz.grade_code("```python\ndef is_palindrome(s):\n    return True\n```", task) == (False, "AssertionError")


def test_questions_cover_all_80_in_order():
    cats = [c for c, _, _ in quiz.questions()]
    assert len(cats) == 80
    assert cats[:20] == ["math"] * 20 and cats[60:] == ["hard"] * 20


def row(category, correct, seconds=1.0, crashed=False, limit=False):
    return {"category": category, "correct": correct, "seconds": seconds, "thinking_chars": 0,
            "hit_token_limit": limit, "crashed": crashed}


def test_summarize_splits_everyday_and_hard_and_skips_crashes_in_timing():
    rows = [row("math", True, 2), row("coding", False, 4, limit=True), row("hard", False, crashed=True), row("hard", True, 6)]
    s = quiz.summarize(rows)
    assert s["overall_pct"] == 50.0 and s["everyday_pct"] == 50.0 and s["hard_pct"] == 50.0
    assert s["knowledge_pct"] is None
    assert s["avg_seconds_per_question"] == 4.0
    assert s["crashed"] == 1 and s["hit_token_limit"] == 1


def model(tag, tps, overall, hard, idle_gb, contexts, max_ctx=131072, **extra):
    return {"tag": tag, "name": tag.title(), "download_gb": 5.0, "max_context_tokens": max_ctx, "memory_gb_idle": idle_gb,
            "speed": {"tokens_per_second": tps}, "quiz": {"overall_pct": overall, "hard_pct": hard}, "by_context": contexts, **extra}


DOC = {"2048": {"prompt_tokens": 1800, "memory_gb": 6.0, "wait_before_first_token_s": 5},
       "131072": {"prompt_tokens": 114000, "memory_gb": 20.0, "wait_before_first_token_s": 900}}


def test_token_counts_are_decimal_thousands():
    assert [summarize.k_tokens(n) for n in (1838, 2048, 8192, 28844, 32768, 131072, 262144)] == \
        ["1.8K", "2.0K", "8.2K", "29K", "33K", "131K", "262K"]
    header = summarize.markdown_tables([model("s", 1, 1, 1, 1, DOC)])[0].splitlines()[0]
    assert header == "| Model | Engine | Format | Download | Context window | Memory @ 2.0K | Memory @ 131K | Wait @ 2.0K | Wait @ 131K |"


def test_markdown_tables_mark_crashes_over_max_and_other_ollama_versions():
    crashy = model("q", 14, 91, 70, 18, {"2048": {"crashed": True}, "262144": {"crashed": True}}, max_ctx=262144, ollama_version="0.35.1")
    small = model("s", 28, 72, 25, 6, DOC, ollama_version="0.40.3", runner="llama.cpp", quantization="Q4_K_M")
    memory, speed = summarize.markdown_tables([crashy, small, {**small, "tag": "t", "name": "T"}])
    assert "| Q | – | – | 5.0 GB | 262K tokens | crashes | – | crashes | crashes | – | crashes |" in memory
    assert "| S | older | Q4_K_M | 5.0 GB | 131K tokens | 6.0 GB | 20.0 GB | over max | 5 s | 15.0 min | over max |" in memory
    assert speed.splitlines()[2].startswith("| Q |")
    assert "Q was measured on Ollama 0.35.1, the others on 0.40.3." in speed and "S was measured" not in speed


def test_wait_switches_to_minutes_then_hours():
    assert [summarize.wait(s) for s in (None, 22.1, 379.6, 7785.2)] == ["–", "22 s", "6.3 min", "2.2 hours"]


def test_fill_replaces_only_between_markers(tmp_path: pathlib.Path):
    f = tmp_path / "x.md"
    f.write_text("before\n<!-- t:start -->\nold\n<!-- t:end -->\nafter\n")
    summarize.fill(f, "t", "new")
    assert f.read_text() == "before\n<!-- t:start -->\nnew\n<!-- t:end -->\nafter\n"


# The tests below use the local machine and the local Ollama server (read-only calls), not mocks.
from bench import ollama_client, speed


def test_document_text_is_real_source_of_requested_length():
    text = speed.document_text(5000)
    assert len(text) == 5000 and "def " in text


def test_environment_describes_this_machine():
    env = speed.environment()
    assert env["chip"].startswith("Apple") and env["memory"] == "64 GB"


def test_client_targets_the_server_named_by_ollama_host(monkeypatch):
    import importlib
    monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1:11435")
    assert importlib.reload(ollama_client).OLLAMA == "http://127.0.0.1:11435"
    monkeypatch.delenv("OLLAMA_HOST")
    assert importlib.reload(ollama_client).OLLAMA == "http://localhost:11434"


def test_installed_models_and_model_facts_come_from_ollama():
    tags = ollama_client.installed_models()
    assert "deepseek-r1:latest" in tags
    facts = summarize.model_facts("deepseek-r1:latest")
    assert facts["max_context_tokens"] == 131072 and 8 < facts["params_b"] < 9 and facts["download_gb"] > 4


def test_runner_memory_is_none_or_plausible():
    gb = ollama_client.runner_memory_gb()
    assert gb is None or 0.5 < gb < 64
    mem = ollama_client.runner_memory()
    assert mem is None or mem[1] >= mem[0]


def test_process_peak_counts_only_memory_used_after_reset():
    import subprocess, time
    child = subprocess.Popen([sys.executable, "-c",
                              "import mmap, time\n"
                              "def touch(n):\n"
                              "    m = mmap.mmap(-1, n)\n"
                              "    for i in range(0, n, 16384): m[i] = 1\n"
                              "    return m\n"
                              "touch(400_000_000).close(); time.sleep(1.5); b = touch(100_000_000); time.sleep(5)"])
    try:
        time.sleep(1)
        assert ollama_client.process_memory(child.pid)[1] > 400e6
        ollama_client.reset_peak(child.pid)
        assert ollama_client.process_memory(child.pid)[1] < 50e6
        time.sleep(1.5)
        assert 100e6 < ollama_client.process_memory(child.pid)[1] < 200e6
    finally:
        child.kill()


def test_peak_memory_keeps_the_highest_current_or_kernel_peak(monkeypatch):
    import time
    samples = iter([(5e9, 6e9), (9e9, 9e9), (7e9, 12e9)])
    monkeypatch.setattr(ollama_client, "runner_pid", lambda model=None: None)
    monkeypatch.setattr(ollama_client, "runner_memory", lambda model=None: next(samples, (4e9, 4e9)))
    with ollama_client.PeakMemory("m", interval=0.01) as peak:
        time.sleep(0.1)
    assert peak.gb == 12.0
    monkeypatch.setattr(ollama_client, "runner_memory", lambda model=None: None)
    with ollama_client.PeakMemory("m", interval=0.01) as none:
        pass
    assert none.gb is None


def test_regrade_rescores_saved_replies_only():
    good = f"```python\n{CODING[0]['ref']}\n```"
    rows = [{"n": 41, "category": "coding", "correct": False, "detail": "old", "response": good, "seconds": 1,
             "thinking_chars": 0, "hit_token_limit": False},
            {"n": 1, "category": "math", "correct": True, "detail": "30.5", "seconds": 1, "thinking_chars": 0, "hit_token_limit": False}]
    data = {"models": {"m": {"questions": rows}}}
    quiz.regrade(data)
    assert rows[0]["correct"] and rows[0]["detail"] == "pass" and rows[1]["correct"]
    assert data["models"]["m"]["summary"]["overall_pct"] == 100.0


# Consistency: every number in the docs must match the measured data or the script settings.
import json
import re

ROOT = pathlib.Path(__file__).parent.parent
DATA = json.loads((ROOT / "benchmarks.json").read_text())
README, DECK = ((ROOT / f).read_text() for f in ("README.md", "index.html"))


def test_generated_doc_sections_match_benchmarks_json():
    models = DATA["models"]
    memory, speed_md = summarize.markdown_tables(models)
    assert memory in README and speed_md in README
    assert (ROOT / "benchmarks.js").read_text().endswith("window.BENCHMARKS = " + json.dumps(DATA, indent=2) + ";\n")


def test_hand_written_numbers_match_settings_and_machine():
    m = DATA["machine"]
    from collections import Counter
    counts = Counter(c for c, _, _ in quiz.challenge_questions())
    n = sum(counts.values())
    for doc in (README, DECK):
        assert f"{n}-question challenge set" in doc
        assert f"{counts['math']} math" in doc and f"{counts['coding']} coding" in doc.replace("Python coding", "coding")
        assert "80-question quiz" not in doc.replace("an earlier 80-question quiz", "")
    assert f"Ollama {m['ollama_version']}" in README
    assert f"{speed.GEN_TOKENS}-token answer" in README
    assert f"{quiz.MAX_TOKENS:,} tokens" in README and f"{quiz.MAX_TOKENS:,} tokens" in DECK
    assert f"Median of {speed.RUNS} runs" in README
    assert m["model_identifier"] in README and "14-inch" in README and "14-inch" in DECK
    assert f"{m['gpu_memory_limit_gb']} GB" in README
    assert m["memory"] == "64 GB" and m["memory_gb"] == round(64 * 2**30 / 1e9, 1) == 68.7
    assert "64 GiB" in README and f"{m['memory_gb']} GB" in README
    assert "64 GiB" in DECK and "ramGb" in DECK and "of the 64 GB" not in DECK


def test_every_model_was_measured_on_one_ollama_version():
    assert {m["ollama_version"] for m in DATA["models"]} == {DATA["machine"]["ollama_version"]}


def test_audience_facing_text_has_no_jargon():
    visible = re.sub(r"<style>.*?</style>|<script.*?</script>", "", DECK, flags=re.S)
    notes = DECK[DECK.index("function notes()"):DECK.index("// ---------- Navigation")]
    for text in (visible, notes, README):
        text = re.sub(r"ollama run \S+", "", text)  # a model's tag is what the audience types, jargon or not
        for term in ("MLX", "llama.cpp", "KV cache", "prefill", "Pareto", "mixture-of-experts", "panic"):
            assert term.lower() not in text.lower(), term


def test_deck_and_python_round_numbers_the_same_way():
    import subprocess
    fmt_js = next(l for l in DECK.splitlines() if l.strip().startswith("const fmt ="))
    values = [72.5, 97.5, 98.75, 0.15, 24.78, 13.7, 2.36, 1530.43 / 60, 65.0, 0.05]
    js = subprocess.run(["node", "-e", fmt_js + f"\nfor (const v of {values}) for (const d of [0, 1]) console.log(fmt(v, d));"],
                        capture_output=True, text=True, check=True).stdout.split()
    assert js == [summarize.num(v, d) for v in values for d in (0, 1)]
    k_js = next(l for l in DECK.splitlines() if l.strip().startswith("const kTokens ="))
    counts = [1838, 2048, 9950, 9999, 10000, 28844, 113438.5, 131072, 262144]
    js = subprocess.run(["node", "-e", fmt_js + "\n" + k_js + f"\nfor (const n of {counts}) console.log(kTokens(n));"],
                        capture_output=True, text=True, check=True).stdout.split()
    assert js == [summarize.k_tokens(n) for n in counts]


def test_memory_slide_tooltips_use_measured_numbers_only():
    growth = DECK[DECK.index("function renderGrowth()"):DECK.index("function renderGrowthLabels()")]
    assert not re.search(r"~\s*\d|\d[\d,.]*\s*(K\b|tokens|GB)", growth), "hand-written token or GB number in the Memory slide"
    assert "prompt_tokens" in growth and "reply_tokens" in growth and "memAt(EXAMPLE" in growth


def test_no_binary_thousands_in_token_counts():
    """128K and 256K are binary (131,072 and 262,144). Shown token counts use decimal thousands."""
    # A window that really is 128,000 or 256,000 tokens (LFM2.5's is 128,000) is shown as 128K or 256K, correctly.
    decimal = [f"{summarize.k_tokens(m['max_context_tokens'])} tokens" for m in DATA["models"] if m["max_context_tokens"] in (128000, 256000)]
    for text in (README, DECK, json.dumps(DATA)):
        for label in decimal:
            text = text.replace(label, "")
        assert not re.search(r"\b(128|256)K\b", text)
    assert "1024" not in DECK


def test_tokens_per_word_rule_of_thumb_holds_for_english_prose():
    """The deck says 1,000 tokens is about 750 English words. Check it with a real tokenizer on ordinary prose."""
    import subprocess
    raw = subprocess.run("man less | col -b", shell=True, capture_output=True, text=True).stdout
    lines = [l.strip() for l in raw.splitlines() if len(l.split()) >= 6 and sum(c.isalpha() or c.isspace() for c in l) / len(l) > 0.9]
    text = " ".join(lines)[:8000]
    tokens = ollama_client.post("/api/generate", {"model": "gemma4:latest", "prompt": text, "raw": True, "stream": False,
                                                 "options": {"num_predict": 1}})["prompt_eval_count"]
    words_per_1000 = 1000 * len(text.split()) / tokens
    assert 700 <= words_per_1000 <= 850, words_per_1000
    assert "1,000 tokens is about 750 English words" in DECK


def test_audit_measured_values_match_benchmarks_json():
    audit = (ROOT / "LANDING.md").read_text()
    by_tag = {m["tag"]: m for m in DATA["models"]}
    for tag, code in (("deepseek-r1:latest", "A1"), ("gemma4:latest", "A2"), ("qwen3.8:27b", "A3"), ("qwen3.5:35b", "A4")):
        row = next(l for l in audit.splitlines() if l.startswith(f"| {code} |"))
        assert f"| {summarize.num(by_tag[tag]['speed']['tokens_per_second'], 1)} tokens/sec |" in row, row
    assert f"measured on Ollama {by_tag['qwen3.8:27b']['ollama_version']}" in audit
    assert f"ran out of room on {by_tag['deepseek-r1:latest']['quiz']['hit_token_limit']} answers" in audit
    peak = lambda tag: summarize.num(by_tag[tag]["by_context"]["262144"]["memory_gb"], 1)
    assert f"Qwen 3.5 35B at 262K peaks at {peak('qwen3.5:35b')} GB" in audit
    assert audit.count(f"peaked at {peak('qwen3.8:27b')} GB") == 2
    share = round(by_tag["qwen3.8:27b"]["by_context"]["262144"]["memory_gb"] / DATA["machine"]["memory_gb"] * 100)
    assert f"{share}% of the Mac's {DATA['machine']['memory_gb']} GB" in audit


def test_voice_summary_splits_the_middle_turn_into_stages():
    turn = lambda v2v, llm: {"voice_to_voice_ms": v2v, "hangover_ms": 400, "stt_ms": 50, "llm_ms": llm, "tts_ms": 60}
    s = summarize.voice_summary([turn(900, 380), {"turn": 9}, turn(700, 180), turn(800, 285)])
    assert (s["turns"], s["min_ms"], s["median_ms"], s["max_ms"]) == (3, 700, 800, 900)
    assert s["median_turn_stages_ms"] == {"hangover_ms": 400, "stt_ms": 50, "llm_ms": 285, "tts_ms": 60, "other_ms": 5}


def test_voice_numbers_come_from_the_session_log():
    v = DATA["voice"]
    assert v == summarize.load_voice()
    assert v["model"] in {m["tag"] for m in DATA["models"]}
    assert v["ollama_version"] in README


# Layout: every slide, shown with the deck's own go(), must fit common presentation screens.
CHROME = pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
LAYOUT_PAGE = """<!doctype html><body style="margin:0"><pre id="out">running</pre><script>
const sizes = [[1280, 720], [1440, 900], [1920, 1080]], out = [];
const wait = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  for (const [w, h] of sizes) {
    const f = document.createElement("iframe");
    f.style.cssText = `width:${w}px;height:${h}px;border:0;display:block`;
    f.src = "index.html";
    document.body.append(f);
    await new Promise(r => f.onload = r);
    const win = f.contentWindow, slides = [...win.document.querySelectorAll(".slide")];
    for (let i = 0; i < slides.length; i++) {
      win.go(i);
      await wait(1200);  // past the bars' entry animation
      const s = slides[i];
      // Slides with a document-size picker are checked at every size, since row labels and notes change with it.
      const picks = s.querySelectorAll("#ctxPicker button").length || 1;
      for (let p = 0; p < picks; p++) {
        s.querySelectorAll("#ctxPicker button")[p]?.click();
        await wait(100);
        // Panels that scroll inside the slide hide content too, so count the worst of the slide and its scroll boxes.
        const boxes = [s, ...[...s.querySelectorAll("*")].filter(e => /auto|scroll/.test(win.getComputedStyle(e).overflowY))];
        const worst = k => Math.max(...boxes.map(b => k === "y" ? b.scrollHeight - b.clientHeight : b.scrollWidth - b.clientWidth));
        out.push(`${w}x${h} ${s.dataset.title}${picks > 1 ? " #" + p : ""}: ${worst("y")} ${worst("x")}`);
      }
    }
    f.remove();
  }
  document.getElementById("out").textContent = out.join("\\n");
})().catch(e => document.getElementById("out").textContent = "error: " + e);
</script></body>"""


def test_every_slide_fits_common_screens():
    import functools, http.server, pytest, subprocess, threading
    if not CHROME.exists():
        pytest.skip("Google Chrome is not installed")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/layout.html":
                return super().do_GET()
            body = LAYOUT_PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        dom = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-first-run", "--window-size=1920,1080",
                              "--virtual-time-budget=120000", "--dump-dom", f"http://127.0.0.1:{server.server_port}/layout.html"],
                             capture_output=True, text=True, timeout=180).stdout
    finally:
        server.shutdown()
    rows = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S).group(1).strip().splitlines()
    assert len(rows) == 3 * (len(re.findall(r'<section class="slide"', DECK)) - 1 + 5), rows  # all slides, with five What fits variants
    # scrollHeight and clientHeight are each rounded to whole pixels, so 1 px is rounding, not hidden content.
    overflowing = [r for r in rows if max(map(int, r.rsplit(":", 1)[1].split())) > 1]
    assert not overflowing, overflowing


def test_baked_system_prompt_is_replaced_by_an_empty_one():
    assert ollama_client.messages("Q", baked_system=False) == [{"role": "user", "content": "Q"}]
    assert ollama_client.messages("Q", baked_system=True) == [{"role": "system", "content": ""}, {"role": "user", "content": "Q"}]


def test_same_text_documents_fit_every_measured_tokenizer():
    # Densest tokenizer measured on this document (Gemma 4, 3.44 chars/token) must still leave room for the reply.
    for ctx in (2048, 8192, 32768, 131072, 262144):
        assert speed.same_text_chars(ctx) / 3.44 + speed.REPLY_TOKENS < ctx
    assert speed.same_text_chars(262144) == 754974


def test_runner_is_found_for_bundled_and_standalone_ollama():
    app = "101 /Applications/Ollama.app/Contents/Resources/llama-server --model /x/blobs/sha256-a --port 1"
    standalone = "202 /tmp/scratch/ollama-0.40.6/llama-server --model /x/blobs/sha256-b --port 2"
    mlx = "303 /tmp/scratch/ollama-0.40.6/ollama runner --mlx-engine --model gemma4:12b --port 3"
    shell = "404 /bin/zsh -c grep llama-server"
    assert ollama_client.find_runner(app) == 101
    assert ollama_client.find_runner(f"{shell}\n{standalone}") == 202
    assert ollama_client.find_runner(mlx, "gemma4:12b") == 303
    assert ollama_client.find_runner(mlx, "qwen3.8:27b") is None
    assert ollama_client.find_runner(shell) is None


def test_challenge_set_keys_grade_as_correct_and_keep_the_intended_questions():
    from bench.quiz_questions import CHALLENGE_CODING, CHALLENGE_KEEP, CHALLENGE_MATH, CHALLENGE_MULTIPLE_CHOICE
    qs = list(quiz.challenge_questions())
    assert len(qs) == len(CHALLENGE_KEEP) + len(CHALLENGE_MATH) + len(CHALLENGE_MULTIPLE_CHOICE) + len(CHALLENGE_CODING)
    main = list(quiz.questions())
    assert [p for _, p, _ in qs[:len(CHALLENGE_KEEP)]] == [main[n - 1][1] for n in CHALLENGE_KEEP]
    assert "sum of the digits of 2 to the power of 100" in qs[CHALLENGE_KEEP.index(63)][1]
    new = qs[len(CHALLENGE_KEEP):]
    math_q, mc_q, code_q = new[:len(CHALLENGE_MATH)], new[len(CHALLENGE_MATH):-len(CHALLENGE_CODING)], new[-len(CHALLENGE_CODING):]
    for (_, _, grade), (_, answer) in zip(math_q, CHALLENGE_MATH):
        assert grade(f"Work.\nANSWER: {answer}")[0] and not grade(f"ANSWER: {answer + 1}")[0]
    for (_, _, grade), (_, _, letter) in zip(mc_q, CHALLENGE_MULTIPLE_CHOICE):
        assert grade(f"ANSWER: {letter}")[0] and not grade("ANSWER: " + ("A" if letter != "A" else "B"))[0]
    for (_, _, grade), task in zip(code_q, CHALLENGE_CODING):
        assert grade(f"```python\n{task['ref']}\n```")[0], task["name"]
        assert not grade(f"```python\ndef {task['name']}(*a, **k):\n    return None\n```")[0], task["name"]


def test_regrade_uses_the_question_set_saved_with_the_results():
    g = quiz.challenge_questions.__globals__
    first_new, answer = len(g["CHALLENGE_KEEP"]) + 1, g["CHALLENGE_MATH"][0][1]
    data = {"settings": {"set": "challenge"}, "models": {"m": {"questions": [
        {"n": first_new, "category": "math", "correct": False, "response": f"ANSWER: {answer}", "seconds": 1, "tokens": 1,
         "thinking_chars": 0, "hit_token_limit": False}]}}}
    quiz.regrade(data)
    assert data["models"]["m"]["questions"][0]["correct"] is True


def test_tradeoffs_measured_cells_match_the_data_and_estimates_are_marked():
    """Measured cells come from the saved runs. The M5 Max column is an estimate, and only appears marked as one."""
    run = json.loads((ROOT / "bench/results/openrouter-qwen38-27b.json").read_text())
    cost = sum(q["usage"]["cost"] for q in run["questions"])
    gpu = json.loads((ROOT / "bench/results/l40s-qwen38-27b.json").read_text())["summary"]
    q = next(m for m in DATA["models"] if m["tag"] == "qwen3.8:27b")
    assert f"${cost:.3f} for 29 questions" in DECK
    assert f"{summarize.num(run['summary']['median_completion_tokens_per_total_second'], 0)} tokens/sec, including network" in DECK
    assert f"{summarize.num(gpu['median_completion_tokens_per_total_second'], 0)} tokens/sec, including network" in DECK
    for estimate in ("About $5,099", "About 21 to 25 tokens/sec", "About 30 min"):
        assert f'<td class="expected">{estimate}</td>' in DECK


def test_environment_table_matches_the_saved_runs():
    """The three-environment slide carries exactly what publish_environments.py builds from the results."""
    from bench import publish_environments as env
    table = env.rows()
    assert env.html(table) in DECK
    gpu_qwen = next(r for r in table if r["model"] == "Qwen 3.8 27B" and r["where"] == "Rented L40S")
    assert gpu_qwen["wait_262k"] == "too long"


def test_mac_document_fallback_is_the_native_measurement_and_marked():
    """A Mac document size the shared client could not finish shows the Oct 22 native wait, marked and footnoted."""
    from bench import publish_environments as env
    mac_qwen = next(r for r in env.rows() if r["model"] == "Qwen 3.8 27B" and r["where"] == "This Mac")
    native = next(m for m in DATA["models"] if m["tag"] == "qwen3.8:27b")["by_context"]["262144"]["wait_before_first_token_s"]
    assert mac_qwen["wait_262k"] == summarize.wait(native) + env.NATIVE
    assert env.NATIVE_NOTE in DECK

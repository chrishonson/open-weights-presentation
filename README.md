# Open-Weight AI: Laptop, GPU and API

A presentation on running open-weight AI on an M1 Max MacBook Pro, an AWS L40S GPU, and through OpenRouter / DeepInfra. Four selected models ran on Mac and L40S; two also ran through the API. Start with [LANDING.md](LANDING.md) for the decisions, results, methods and caveats. All measured results come from scripts and saved responses in `bench/`.

## Files

| File | What it is |
| :--- | :--- |
| `index.html` | The interactive slide deck. Local numbers come from `benchmarks.js`; deployment tables are generated from saved Mac, AWS and OpenRouter runs. |
| `benchmarks.json` | Local measured results. Generated, do not edit by hand. |
| `benchmarks.js` | The same data wrapped for the HTML deck. Generated. |
| `GPU-RUN.md` | Runbook and results for the completed AWS GPU comparison using `bench/venue.py`. |
| `bench/` | The benchmark scripts, the quiz, and raw results. |
| `LANDING.md` | Everything for finishing the talk: decisions, how to rebuild and check it, results, methods, claim sources, caveats and state. |
| `DEMO.md` | Runbook for the live voice demo at the end of the talk. `demo/live-demo.toml` is its ships-computer config. |
| `OPENROUTER.md` | Results and rerun commands for Gemma 4 26B (FP8) and Qwen 3.8 27B (BF16) on OpenRouter / DeepInfra. |

## Present it

```bash
open index.html
```

Keys: `←` `→` or `Space` to move, `N` for speaker notes, `F` for full screen, `1` to `9` to jump to the first nine slides. `index.html#4` opens slide 4 directly.

OpenRouter is slide 10 (`index.html#10`); the three-environment answers and document waits follow on slides 11–12. Refresh its table and speaker notes without contacting any model:

```bash
python3 bench/publish_openrouter.py
```

This is also called by `bench/summarize.py`. The two hosted result files remain separate from the local speed chart.

Definitions are on slides 2–3; hardware context is on slides 4–6. API economics follows the OpenRouter API slide. Prices, specifications and offline image credits are in `HARDWARE-SOURCES.md`.

## The machine

MacBook Pro 14-inch (2021, `MacBookPro18,4`), Apple M1 Max (10 CPU cores, 32 GPU cores), 64 GB unified memory (Apple's 64 GB is 64 GiB = 68,719,476,736 bytes = 68.7 GB), 400 GB/s memory bandwidth (Apple spec). macOS recommends the GPU use at most 55.7 GB, which is 51.8 GiB (`recommendedMaxWorkingSetSize`, measured). Ollama 0.40.6 for every model, on macOS 26.5.2, on AC power.

## Earlier Mac-only survey (October 22)

The newer client-timed comparison is in the deck and LANDING.md. These historical survey tables use different timing definitions; 131K/262K column labels are target test-size identifiers, not each model’s actual input token counts.

The README lists all 15 measured models. The deck shows the 9 marked `in_deck` in `bench/models.json`.

<!-- tables:start -->
### Memory and waiting time

| Model | Engine | Format | Download | Context window | Memory @ 2.0K | Memory @ 8.2K | Memory @ 33K | Memory @ 131K | Memory @ 262K | Wait @ 2.0K | Wait @ 8.2K | Wait @ 33K | Wait @ 131K | Wait @ 262K |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek-R1 8B | older | Q4_K_M | 5.2 GB | 131K tokens | 6.3 GB | 8.5 GB | 10.4 GB | 25.0 GB | over max | 5 s | 22 s | 2.0 min | 17.8 min | over max |
| Gemma 4 E2B | newer | nvfp4 | 7.5 GB | 131K tokens | 8.8 GB | 9.0 GB | 9.1 GB | 10.5 GB | over max | 0 s | 2 s | 9 s | 1.1 min | over max |
| Gemma 4 E4B | newer | nvfp4 | 9.5 GB | 131K tokens | 10.8 GB | 11.3 GB | 11.8 GB | 14.9 GB | over max | 2 s | 7 s | 30 s | 2.6 min | over max |
| Gemma 4 12B | newer | nvfp4 | 7.7 GB | 262K tokens | 11.2 GB | 12.8 GB | 12.7 GB | 19.2 GB | 28.1 GB | 9 s | 36 s | 2.4 min | 12.8 min | 37.6 min |
| Gemma 4 26B | newer | nvfp4 | 16.1 GB | 262K tokens | 18.9 GB | 20.3 GB | 20.6 GB | 26.3 GB | 34.7 GB | 3 s | 13 s | 56 s | 5.7 min | 18.0 min |
| Qwen 3.5 4B | newer | nvfp4 | 4.0 GB | 262K tokens | 6.5 GB | 7.5 GB | 9.3 GB | 19.5 GB | 34.3 GB | 3 s | 10 s | 44 s | 4.7 min | 15.7 min |
| Qwen 3.5 35B | newer | nvfp4 | 21.9 GB | 262K tokens | 24.8 GB | 25.6 GB | 27.0 GB | 35.5 GB | 47.9 GB | 2 s | 9 s | 41 s | 5.1 min | 18.6 min |
| Qwen 3.8 27B | newer | nvfp4 | 18.2 GB | 262K tokens | 23.5 GB | 26.0 GB | 32.3 GB | 53.0 GB | 59.6 GB | 20 s | 1.3 min | 5.2 min | 29.2 min | 1.8 hours |
| Qwen 3.8 27B Q4_K_M | older | Q4_K_M | 17.7 GB | 262K tokens | 19.7 GB | 22.1 GB | 20.9 GB | 28.6 GB | 37.2 GB | 18 s | 1.3 min | 5.3 min | 28.0 min | 1.5 hours |
| Qwen 3.8 27B redteam | older | Q4_K_M | 16.6 GB | 262K tokens | 18.3 GB | 19.7 GB | 20.6 GB | 27.2 GB | 36.1 GB | 18 s | 1.3 min | 5.3 min | 28.0 min | 1.5 hours |
| Nemotron 3.5 Lightning | newer | nvfp4 | 19.1 GB | 262K tokens | 22.4 GB | 22.8 GB | 22.6 GB | 38.4 GB | crashes | 3 s | 12 s | 52 s | 4.9 min | crashes |
| OLMo 3 7B | older | Q4_K_M | 4.5 GB | 66K tokens | 10.7 GB | 16.7 GB | 14.3 GB | over max | over max | 5 s | 24 s | 1.6 min | over max | over max |
| SmolLM3 3B | older | Q4_K_M | 1.9 GB | 66K tokens | 2.5 GB | 3.7 GB | 4.6 GB | over max | over max | 2 s | 9 s | 50 s | over max | over max |
| LFM2.5 8B-A1B | older | Q4_K_M | 5.2 GB | 128K tokens | 5.4 GB | 5.7 GB | 5.9 GB | 7.8 GB | over max | 1 s | 4 s | 20 s | 2.3 min | over max |
| Bonsai 2 4B | older | Q2_0 | 1.6 GB | 262K tokens | 2.7 GB | 3.2 GB | 3.4 GB | 7.5 GB | 12.6 GB | 2 s | 10 s | 45 s | 6.4 min | 24.0 min |
| Bonsai 2 9B | older | Q2_0 | 3.2 GB | 262K tokens | 4.4 GB | 5.0 GB | 5.1 GB | 8.4 GB | 12.9 GB | 4 s | 18 s | 1.3 min | 7.3 min | 24.1 min |
| Bonsai 2 27B | older | Q2_0 | 8.3 GB | 262K tokens | 10.6 GB | 11.8 GB | 11.7 GB | 18.6 GB | 27.4 GB | 16 s | 1.1 min | 4.8 min | 25.0 min | 1.4 hours |

### Speed and accuracy

| Model | Writing speed (tokens/sec) | Challenge (29) | Math (14) | Coding (12) | Avg. time per answer |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.8 27B Q4_K_M | 8 | 100% | 100% | 100% | 2.3 min |
| Gemma 4 26B | 54 | 93% | 93% | 92% | 13 s |
| Qwen 3.8 27B | 14 | 93% | 93% | 92% | 58 s |
| Qwen 3.8 27B redteam | 8 | 93% | 86% | 100% | 2.7 min |
| Qwen 3.5 35B | 58 | 83% | 100% | 67% | 20 s |
| Bonsai 2 27B | 14 | 83% | 86% | 75% | 1.2 min |
| Gemma 4 12B | 28 | 79% | 86% | 67% | 33 s |
| Nemotron 3.5 Lightning | 66 | 79% | 79% | 75% | 7 s |
| Qwen 3.5 4B | 65 | 72% | 79% | 67% | 21 s |
| LFM2.5 8B-A1B | 151 | 69% | 79% | 50% | 18 s |
| Gemma 4 E4B | 65 | 66% | 79% | 50% | 14 s |
| Bonsai 2 9B | 39 | 66% | 86% | 42% | 39 s |
| Bonsai 2 4B | 71 | 62% | 71% | 42% | 13 s |
| Gemma 4 E2B | 95 | 55% | 64% | 42% | 10 s |
| OLMo 3 7B | 28 | 52% | 64% | 42% | 33 s |
| SmolLM3 3B | 62 | 48% | 57% | 42% | 6 s |
| DeepSeek-R1 8B | 28 | 17% | 0% | 25% | 3.6 min |

DeepSeek-R1 8B ran out of room on 23 answers, which count as wrong. Gemma 4 E2B ran out of room on 2 answers, which count as wrong. Gemma 4 12B ran out of room on 2 answers, which count as wrong. Qwen 3.5 4B ran out of room on 2 answers, which count as wrong. Qwen 3.8 27B redteam ran out of room on 1 answer, which counts as wrong. OLMo 3 7B ran out of room on 1 answer, which counts as wrong. LFM2.5 8B-A1B ran out of room on 3 answers, which count as wrong.
<!-- tables:end -->

## How it was measured

- **Speed.** Ollama's own timings (`eval_count / eval_duration`). Median of 3 runs of a 300-token answer at temperature 0.
- **Waiting time and reading speed.** A document of Python standard-library source code of each size, with a unique first line so nothing is cached. Waiting time is Ollama's `prompt_eval_duration`.
- **Memory.** The most memory Ollama's model process used while it read the document. This includes the model, its short-term memory and the working space it needs while reading, which is freed afterwards. Each document is read by a freshly started process, and the peak is counted from after the model has loaded, so neither earlier documents nor the brief spike of loading the model are included. macOS has two ways to report memory, and each one misses part of it for one of Ollama's two engines, so we take the larger of the two, sampled every half second, plus the kernel's own record of the process's peak (see `PeakMemory` in `bench/ollama_client.py`).
- **Accuracy.** A 29-question challenge set written for this deck (`bench/quiz_questions.py`, `quiz.py --set challenge`): 14 math problems, 3 multiple-choice logic questions and 12 Python coding tasks. 15 come from an earlier 80-question quiz and the rest are new. Questions every model answered correctly are left out, so the set separates models. Math and multiple choice are graded by exact match on a final `ANSWER:` line. Code is graded by running unit tests. Temperature 0, thinking off, at most 6,144 tokens per answer (a cut-off answer counts as wrong). DeepSeek-R1 cannot turn thinking off, so its answers include thinking. Every reply is saved in `bench/results/challenge.json`.
- **Voice.** From [ships-computer](https://github.com/chrishonson/ships-computer), a separate project on the same laptop: Parakeet v3 speech to text, `gemma4:latest`, Pocket TTS, with Smart Turn v3 endpoint detection and a 300 ms hangover. One scripted session of recorded speech fed in real time (`demo/live-demo.toml`), copied to `bench/results/voice/`. Voice to voice is from the end of speech to the first reply audio. The deck shows the middle turn split into its stages. This session ran on Ollama 0.40.10.
- **Ollama defaults.** No tuning. Ollama's newer engine guesses a few tokens ahead by default, and that is part of the measured speed.

- **Rules of thumb in the deck.** "1,000 tokens is about 750 English words" was checked on this machine: ordinary English prose came out at 750 to 807 words per 1,000 tokens with the Gemma 4 and Qwen 3.5 tokenizers. "Most people read about 5 tokens per second" uses the average adult silent reading speed for English non-fiction, 238 words per minute (Brysbaert, 2019, *Journal of Memory and Language* 109, 104047, a review of 190 studies). That is 3.97 words per second, or 4.9 to 5.3 tokens per second at the measured ratio.
- **Quoted, not measured.** Release dates (from the makers' announcements), Apple's 400 GB/s memory-speed figure, and Qwen 3.5's "about 3B of 35B parameters active" (the "A3B" in its name).

Limits: one machine, a small test (each question is worth about 3 points, so a gap of one or two questions is noise), compressed model downloads, thinking off. DeepSeek-R1, LFM2.5, the Bonsai 2 models and the two Qwen 3.8 27B GGUF downloads run on Ollama's older engine and the other models on its newer one, so some speed differences come from the engine. Nemotron 3.5 Lightning's model process crashed on the huge document on 2026-10-20 and again on 2026-10-22 (`bench/results/night-runner.log`). Qwen 3.8 27B redteam (`rafw007/qwen3.8-27b-redteam`) is a community copy with its safety training removed.

## Re-run the benchmarks

```bash
python3 bench/quiz_questions.py
```

```bash
python3 bench/speed.py --same-text --contexts 2048,8192,32768,131072 --results bench/results/night2-speed.json
```

```bash
python3 bench/quiz.py --set challenge --results bench/results/challenge.json
```

```bash
python3 bench/summarize.py
```

`quiz_questions.py` checks the answer key and reference solutions. `speed.py` and `quiz.py` take model tags as arguments and default to every installed model. `quiz.py --category hard` re-runs one section, and `quiz.py --regrade` re-scores saved replies without asking the models again. `summarize.py` rebuilds `benchmarks.json`, `benchmarks.js`, `bench/results/tables.md` and the tables in `README.md`. Model names, makers and release dates live in `bench/models.json`. To measure on a second Ollama version, start it on another port and set `OLLAMA_HOST` (for example `OLLAMA_HOST=127.0.0.1:11435`). Each model records the version that measured it. Run `summarize.py` against Ollama 0.40.6 (`OLLAMA_HOST=127.0.0.1:11436`), because Ollama 0.40.3 cannot read the Bonsai 2 files.


## Completed three-environment review (October 25)

See [LANDING.md](LANDING.md) for the data audit and interpretation. The earlier Mac-only survey below is separate from the newer client-timed comparison: its internal decoder speed must not be compared directly to full-request output rates. In the newer document runs, Mac Qwen failed at the largest size and Nemotron succeeded; the earlier survey remains preserved as historical evidence. The 131K/262K native table headings are test-size identifiers, not each model’s actual input token counts.

Regenerate the deployment slides without network calls:

```sh
python3 bench/publish_openrouter.py
python3 bench/publish_environments.py
```

### Restored slide layout and inference diagrams

The Open weights and Speed and accuracy pages retain the design from `7b4b59f`. Hardware remains directly after the introduction. The Memory page, rendering functions and styling are restored exactly from `7b4b59f`. New OpenRouter and Inference paths pages explain the request routing and shared benchmark client. API economics follows the OpenRouter API slide. Use the named tabs rather than older slide-number references above.

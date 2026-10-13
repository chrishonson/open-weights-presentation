# Landing the presentation

Everything needed to finish this talk from a cold start: what it is, what is decided, how to rebuild and check it, what the results support, and what is left. Current as of 2026-10-26. Update it when the state changes; earlier audits and handoffs are in git history.

## The talk

Running open-weight AI models on a 64 GB MacBook Pro 14-inch (M1 Max), a rented AWS L40S GPU, and through OpenRouter / DeepInfra. Every number is measured by the scripts in `bench/`, and every reply is saved in `bench/results/`. The only live part is the voice demo.

`index.html` is the deck. The slides, by tab:

Intro · Paths (how the harness reaches each environment) · Macs · GPUs · Servers · Weights · Released · Memory · What fits · Speed · Providers · Compare · API · Economics · Docs · Voice · Demo · Tradeoffs · Method · Details.

Speaker notes are keyed by slide title, so reordering slides cannot move notes onto the wrong page. Press `N` in the deck to show them.

## Decisions already made

Do not reopen these without the owner.

- **No recommendations and no conclusion text.** "Let the results speak." Headlines describe what a slide shows, not what to conclude.
- **The redteam model is shown like any other.** `rafw007/qwen3.8-27b-redteam` is not excluded and not explained away. No red-team prompts are ever evaluated; the challenge does not test safety behaviour.
- **No causal explanations the data does not show.**
- **The local survey shows 9 models,** the ones marked `in_deck` in `bench/models.json`, ordered by family then size. The README lists all 15.
- **The three-environment comparison uses four models:** Qwen 3.8 27B, Gemma 4 26B, Nemotron 3.5 Lightning and Qwen 3.8 27B redteam on the Mac and the L40S; Qwen and Gemma also on OpenRouter.
- **Accuracy is the 29-question challenge set only** (14 math, 3 logic, 12 coding).
- **Units are decimal GB only.** Apple's 64 GB is 64 GiB, which is 68.7 GB. The suggested GPU limit is 51.84 GiB, which is 55.7 GB.
- **Thinking is off everywhere** it can be turned off, to match the Mac runs.
- **The L40S is the GPU.** Its 262K fit check is a result, not a gate: Qwen 3.8 27B fits at most 139,552 tokens there.
- **Tokens get a short note on the Memory slide,** not a slide of their own.
- **The demo config has no coding agents** and uses the stock voice `alba`.
- **Commits never carry a co-author line.** Imperative mood, explain why.

## Build, view, test

Rebuild the local survey (needs Ollama 0.40.6, started with `OLLAMA_HOST=127.0.0.1:11436 ./ollama serve` from `~/.local/share/open-weights-bench/ollama-0.40.6`; the Ollama app cannot read the Bonsai 2 files):

```bash
OLLAMA_HOST=127.0.0.1:11436 python3 bench/summarize.py
```

Rebuild the deployment slides from the saved runs, with no network calls:

```bash
python3 bench/publish_openrouter.py && python3 bench/publish_environments.py
```

Run every check: graders, generated numbers against `benchmarks.json`, hand-written numbers against the settings and machine, jargon, speaker-note coverage, and every slide fitting 1280x720, 1440x900 and 1920x1080 in headless Chrome:

```bash
python3 -m pytest bench
```

View the deck over HTTP, because the file view does not load `benchmarks.js`:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/index.html. Hard reload after regenerating. Keys: arrows or Space, `N` notes, `F` full screen. The top tabs navigate.

All new runs, on any server, go through `bench/venue.py`, which times everything from this Mac. `OPENROUTER.md` and `GPU-RUN.md` have the commands.

## Results

| Model | Mac: correct / mean answer | L40S: correct / mean answer | API: correct / mean answer |
| :--- | :--- | :--- | :--- |
| Qwen 3.8 27B | 28/29 · 58.9 s | 28/29 · 50.4 s | 28/29 · 32.4 s |
| Gemma 4 26B | 26/29 · 12.7 s | 28/29 · 8.4 s | 26/29 · 15.1 s |
| Nemotron 3.5 Lightning | 23/29 · 7.9 s | 23/29 · 3.3 s | Not tested |
| Qwen 3.8 27B redteam | 28/29 · 138.6 s | 27/29 · 29.4 s | Not tested |

For the 377,487-character input, Mac first-text waits ranged from 4.7 to 30.3 minutes and L40S waits from 9.2 to 66.8 seconds. At 754,974 characters, Mac Qwen through the shared client was stopped by macOS while the Mac was in use, so the deck shows its October 22 native-API wait, marked with an asterisk. L40S Qwen rejected it as longer than its window. The other three models completed on both machines. Long documents have not been run through OpenRouter.

## Method and comparability

**Two kinds of measurement.** The earlier native Mac survey (`benchmarks.json`, dated October 22) uses Ollama's own durations: writing speed is output tokens over generation time, and the reading wait is prompt-processing time. The three-environment comparison (`mac-venue-*`, `l40s-*`, `openrouter-*` in `bench/results/`) uses client wall time measured on this Mac, including network and the SSH tunnel. Its output rate is completion tokens over total request time. Do not compare the two kinds of throughput directly.

**Settings.** Question runs use temperature 0, seed 0, a 6,144-token output cap and thinking off. That reduces variation but does not guarantee identical execution. A reply cut off at the cap counts as wrong. DeepSeek-R1 cannot turn thinking off.

**Different deployments.** The Mac uses roughly 4-bit builds. The L40S uses FP8 on vLLM 0.32.0, except redteam, which is Q4_K_M on Ollama 0.40.6. Hosted Gemma is FP8 and hosted Qwen BF16, both pinned to DeepInfra with fallbacks off. Engines, precision and templates differ, so no comparison isolates hardware, quantization or engine as the cause of a difference.

**Documents.** Every document is Python standard library source, concatenated, with the request "Explain what the code above does in about 150 words." The 131072 and 262144 context keys are target sizes, not token counts: the inputs are 377,487 and 754,974 characters, about 95K to 104K and 200K to 221K tokens depending on the model. A unique first line defeats caching. This is not a comprehension test, and code token counts should not be turned into English page counts.

**Capacity.** Qwen's 139,552-token L40S limit is specific to that FP8 deployment and its settings, not a limit of the model or of 48 GB GPUs.

**Costs.** The g6e.xlarge rate is about $1.86 an hour, storage excluded. API totals are the recorded usage for these requests: $0.079 for both hosted runs. These billing units do not support a break-even calculation. Power, ownership cost and throughput under load were not measured.

**Small selected challenge.** Each question is worth about 3.4 points. One run per deployment does not support confidence intervals or a ranking.

**Voice.** The 784 ms median is five scripted turns, from end of speech to the first reply audio; speaker delay is excluded.

## Known caveats

- **Release dates lack sources** for Gemma 4 26B, Nemotron 3.5 Lightning and the redteam model. Gemma 4's date conflicts: `models.json` says March 2026, the source below says April 2026. Verify before the talk.
- **Coding items 25 to 29 have not been spot-checked by hand.** Tests confirm every reference solution passes and a stub fails. Read a few failing replies in `bench/results/challenge.json` to rule out a grader bug.
- **Nemotron 3.5 Lightning crashed on the 262K document** in the native survey on 2026-10-20 and 2026-10-22, and succeeded later through the shared client. Both outcomes are kept.
- **DeepSeek-R1 thinks even with thinking off.** In the Memory example its 200 reply tokens per run are all thinking.
- **Peak memory differs by engine.** The nvfp4 Qwen build's 59.6 GB peak at 262K includes about 22 GB of temporary working space.
- **Hardware prices from search results only:** the RTX PRO 5000 ($11,999) and RTX 6000 Ada ($9,605.99) listings were not opened directly. See `HARDWARE-SOURCES.md`.

## Where each claim comes from

| Claim | Where it appears | Evidence |
| :--- | :--- | :--- |
| Every speed, memory, waiting-time and quiz number | deck, README tables | Generated by `bench/summarize.py` from `bench/results/*.json`. `test_generated_doc_sections_match_benchmarks_json` fails if any copy differs. |
| Laptop: 14-inch, M1 Max, 10 CPU cores, 32 GPU cores, 64 GB (64 GiB = 68.7 GB) | deck, README | `system_profiler`. `test_environment_describes_this_machine`, `test_hand_written_numbers_match_settings_and_machine`. |
| macOS recommends the GPU use at most about 56 GB | deck, README | Metal `recommendedMaxWorkingSetSize` = 51.84 GiB = 55.7 GB |
| Memory speed 400 GB per second | deck, README | Apple's published M1 Max spec, labelled "Apple spec" |
| 1,000 tokens is about 750 English words | deck | Measured here: 750–807 words per 1,000 tokens on English prose. `test_tokens_per_word_rule_of_thumb_holds_for_english_prose`. |
| Most people read about 5 tokens per second | deck | 238 words per minute (Brysbaert 2019) = 3.97 words/sec = 4.9–5.3 tokens/sec at the measured ratio |
| Model memory grows with document length, differently per model | deck | `bench/results/speed.json` (memory at each document size) |
| Context window (most text a model can hold: 131K or 262K tokens, in decimal thousands) and how full a document makes it | deck, README | Each model's `context_length` from Ollama (`/api/show`, read by `model_facts` in `bench/summarize.py`). How full: tokens the model actually read (`prompt_tokens`) divided by that limit. |
| Waiting time before the first word | deck, README | Ollama `prompt_eval_duration`, `bench/results/speed.json` |
| Every model measured on Ollama 0.40.6 | deck, README | Each model's results record the Ollama version that measured it. `test_every_model_was_measured_on_one_ollama_version`. |
| Qwen 3.5 35B reads only about 3B parameters per token | deck| Alibaba's model name, Qwen3.5-35B-A3B ("A3B" = 3B active). Quoted, not measured. |
| A bigger model is usually slower | deck, notes | Measured: Qwen 3.8 27B (18.7 GB) 13.7 tok/s vs. DeepSeek-R1 (5.9 GB) 27.5 tok/s. "Usually" because Gemma 4 E4B is bigger than DeepSeek-R1 and faster. |
| Two engines, the newer one guesses tokens ahead | deck, README | `runner` in `bench/models.json`: Ollama `/api/ps` reports `llamacpp` for DeepSeek-R1 and the GGUF downloads (LFM2.5, Bonsai 2, Qwen 3.8 27B Q4_K_M and redteam) and `mlx` for the others. The server log shows speculative-decoding stats for the MLX models. |
| Hosted precision differs from the local builds | deck| Provider endpoint snapshots in the OpenRouter results record FP8 for Gemma and BF16 for Qwen; local builds use nvfp4. |
| A gap of one or two questions is within the noise | deck, notes | Each of 29 questions is worth 3.4 points. At 90% correct the standard error is about 5.6 points |
| DeepSeek-R1 ran out of room on 23 answers | deck | `hit_token_limit` in `bench/results/challenge.json` (6,144-token cap) |
| Release months | deck| Sources in section 3 |
| Runs with no internet once downloaded | deck| Every benchmark call went to `localhost:11434` |
| Voice to voice time and its stages | deck | `bench/results/voice/2026-10-24-135800-live.jsonl`, recorded with the demo config on Ollama 0.40.10. Provenance: `bench/voice.json`. `test_voice_numbers_come_from_the_session_log`. |

## Corrections to the original deck (commit `97556a4`)

| Code | Original claim | What is true | Evidence |
| :--- | :--- | :--- | :--- |
| A1 | DeepSeek-R1 writes 62.0 tokens/sec | 27.5 tokens/sec | `bench/results/night2-speed.json` |
| A2 | Gemma 4 (latest) writes 35.0 tokens/sec | 64.8 tokens/sec | `bench/results/night2-speed.json` |
| A3 | Qwen 3.8 27B writes 21.5 tokens/sec | 13.7 tokens/sec | `bench/results/night2-speed.json` (measured on Ollama 0.40.6) |
| A4 | Qwen 3.5 35B writes 16.0 tokens/sec | 58.1 tokens/sec | `bench/results/night2-speed.json` |
| A5 | Speeds and prefill rates for gpt-oss 20B, Llama 4 Scout, Nemotron 3.5 | None of the three is installed, so nothing could have been measured. Removed. | `ollama list` |
| A6 | MMLU-Pro, HumanEval, MATH-500 and Arena Elo scores for every model | No source given, and Arena Elo cannot be measured on one laptop. Replaced by a 29-question challenge set run here. | `bench/results/challenge.json` (every reply saved) |
| A7 | Llama 4 Scout (109B parameters) uses 28.5 GB | Impossible: 109B parameters at about 4.5 bits each is about 61 GB | arithmetic: 109e9 × 4.5 / 8 bytes |
| A8 | MacBook Pro 16-inch | 14-inch (`MacBookPro18,4`) | `system_profiler SPHardwareDataType` |
| A9 | About 52 GB usable by the GPU | 51.84 GiB = 55.7 GB | Metal `recommendedMaxWorkingSetSize` |
| A10 | Qwen 3.5 35B: dense, 128K context, no vision, Q4_K_M | Mixture of experts (256 experts per layer), 262,144-token context, vision, nvfp4 | `ollama show --verbose qwen3.5:35b` |
| A11 | Gemma 4 (latest): 14B parameters | 8.1B parameters (Gemma 4 E4B, identified by its per-layer embedding tables) | `ollama show --verbose gemma4:latest` |
| A12 | All models Q4_K_M | Only DeepSeek-R1 is Q4_K_M. The other four are nvfp4. | `ollama show` |
| A13 | DeepSeek-R1 released 2026 | May 2025 (`DeepSeek-R1-0528-Qwen3`) | `ollama show --verbose deepseek-r1:latest` (`general.basename`) |
| A14 | Qwen 3.5 35B released mid-2026 | February 2026 | sources in section 3 |
| A15 | Qwen 3.8 27B runs a full 256K context in 46.7 GB | Reading a 203K-token document on Ollama 0.40.6 it peaked at 59.6 GB, over the 55.7 GB macOS recommends and 87% of the Mac's 68.7 GB, and still finished after waiting 1.8 hours. Ollama 0.40.3 crashed with it on documents and long answers, so every model was re-measured on 0.40.6 | `bench/results/night2-speed.json`, `bench/results/night-runner.log`, `bench/results/chain.log` (0.40.3 crashes) |
| A16 | Bandwidth examples: 20 GB → ~19 tok/s, 42.5 GB → ~8.8 tok/s | The deck's own formula gives 15 and 7.1 | arithmetic: 400 / 20 × 0.75, 400 / 42.5 × 0.75 |
| A17 | 70B model needs 41.9 GB extra at 128K | No 70B model is installed. Removed. | `ollama list` |
| A18 | "Pareto frontier" line | The line joined every point, so it was not a frontier. Replaced by marking models no other model beats on both speed and accuracy. | `index.html` (`frontier()`) |
| A19 | Slides overflowed a 1440×900 screen, text down to 10–12 px, chart labels overlapped, jargon (prefill, KV cache, TTFT, Pareto) | Every slide fits 1280×720, 1440×900 and 1920×1080, smallest text about 14 px at 1440×900 (about 12 px at 1280×720), labels placed without overlap, jargon removed | headless Chrome screenshots, `test_every_slide_fits_common_screens` (each slide shown, at all three sizes), `test_audience_facing_text_has_no_jargon` |
| A20 | Memory column: what the model process held after it read the document (this branch, before this fix) | Peak while reading, in a freshly started process, counted from after the model loads. Qwen 3.5 35B at 262K peaks at 47.9 GB, not 31.7 GB, so it is "Fits, little room left", not "Fits easily". Qwen 3.8 27B's old figures fell from 48.7 GB at 131K to 47.4 GB at 262K because they included memory left over from earlier documents | `bench/results/night2-speed.json`, `bench/results/peak-rerun.log` (131K, 262K), `bench/results/peak-rerun-small.log` (2.0K–33K), `PeakMemory` in `bench/ollama_client.py` |
| A21 | macOS lets the graphics chip use up to 56 GB, and a model over it "Does not fit" | 55.7 GB is macOS's recommended maximum, not a hard stop: Qwen 3.8 27B peaked at 59.6 GB at 262K and finished. The verdict now says "Over the suggested limit" | `bench/results/night2-speed.json`, Metal `recommendedMaxWorkingSetSize` |
| A22 | 64 GB of memory, set next to measured sizes in decimal GB | Apple's 64 GB is 64 GiB = 68,719,476,736 bytes = 68.7 GB. The deck mixed the two, so "56 GB of the 64 GB" read as 87% when it is 81%, and a 65.4 GB peak measured then looked larger than the Mac's memory. Every size is now decimal GB and the Mac's memory is stated as 68.7 GB | `sysctl hw.memsize` |

## Sources for quoted facts

- Qwen 3.5 35B (Qwen3.5-35B-A3B), February 2026: [OpenRouter](https://openrouter.ai/qwen/qwen3.5-35b-a3b/apps), [AI Indigo](https://aiindigo.com/blog/ai-arena-qwen35-35b-a3b-release)
- Gemma 4, April 2026, and Gemma 4 12B Unified, June 3, 2026: [Google Gemma release notes](https://ai.google.dev/gemma/docs/releases?hl=en), [Wikipedia](https://en.wikipedia.org/wiki/Gemma_(language_model))
- Qwen 3.8 27B, August 14, 2026: [DataNorth](https://datanorth.ai/news/alibaba-releases-qwen3-8-27b) (secondary coverage)
- Reading speed, 238 words per minute: Brysbaert, M. (2019). How many words do we read per minute? *Journal of Memory and Language* 109, 104047. [Manuscript PDF](https://www.Gwern.net/doc/psychology/linguistics/2019-brysbaert.pdf)

## Repository and infrastructure state

- `main` is the only branch and tracks `origin` (github.com/chrishonson/open-weights-presentation, public). The remote still has the old `deck-merge` and `measured-benchmarks` branches.
- The OpenRouter key is in the git-ignored `.env`.
- The AWS instance and its disk were deleted on 2026-10-26, so nothing bills for compute or EBS. The S3 bucket still holds the 92 GB of model files, and a rerun starts from a fresh launch (`GPU-RUN.md`, which also has the resource IDs).
- `NEXT-STEPS.md` is a local scout report, excluded through `.git/info/exclude`.

## Before the talk

- Verify the release dates above.
- Spot-check the coding grades.
- Rehearse `DEMO.md`, once with Wi-Fi off.
- Optional: run the long-document test through OpenRouter with `bench/venue.py`.

## Working agreements with the owner

- **AWS is a guided-learning track.** One step at a time with a short reason; the owner runs commands, in the console UI where possible. Run AWS commands only when asked.
- **Act on visual feedback directly.** Check every layout change at 1280x720 in a browser and run the tests before reporting.
- **Resume context lives in MetaCortex,** topic `open-weights-presentation`.

# OpenRouter comparison

Models completed an authenticated smoke test, all 29 challenge questions,
three speed runs, and five long-document context runs on 2026-10-24–26. Results are in
`bench/results/openrouter-gemma4-26b.json`, `bench/results/openrouter-qwen38-27b.json`,
and `bench/results/openrouter-haiku55.json`.
The user-provided key is stored in the repository's Git-ignored `.env`, with
file permissions 0600. It is not included in benchmark artifacts.

## Measured result

| Metric | Gemma 4 26B / DeepInfra FP8 | Qwen 3.8 27B / DeepInfra BF16 | Claude Haiku 5.5 / Anthropic API |
| :--- | ---: | ---: | ---: |
| Challenge | 26/29 (89.7%) | 28/29 (96.6%) | 28/29 (96.6%) |
| Average time per challenge answer | 15.1 s | 32.4 s | 2.3 s |
| Median time to first text, three speed requests | 0.307 s | 0.374 s | 0.880 s |
| Median completion tokens / total request seconds | 72.7 | 38.3 | 131.3 |
| Reported cost, challenge only | $0.010263 | $0.067270 | $0.006226 |
| Reported cost, challenge + smoke + speed | $0.010518 | $0.068693 | $0.006688 |

For Gemma, Q16 hit the 6,144-token cap; Q25 failed with a TypeError; Q28 failed
an assertion. Qwen's only failure was Q16, also at the token cap. Haiku's only
failure was logic Q9 (uninformed Monty Hall). All requests used pinned providers
(DeepInfra or Anthropic), with no reported reasoning tokens, request errors, retries,
or provider fallbacks. Total challenge run cost across all three models was $0.085899.

## Selected deployments

| CLI model | OpenRouter model | Pinned endpoint | Precision | Local baseline |
| :--- | :--- | :--- | :--- | :--- |
| `gemma` (default) | `google/gemma-4-26b-a4b-it` | `deepinfra/fp8` | FP8 | `gemma4:26b-nvfp4` |
| `qwen` | `qwen/qwen3.8-27b` | `deepinfra/bf16` | BF16 | `qwen3.8:27b` |
| `haiku` | `anthropic/claude-haiku-5.5` | `anthropic` | API | None (hosted reference) |

Both local builds use nvfp4. The hosted endpoint metadata is captured per run.

- Provider pinned, fallbacks disabled, parameter support required.
- The existing 29 challenge prompts and graders; temperature 0, seed 0,
  reasoning disabled, 6,144 output-token cap. Truncated responses count as wrong.
- Three speed requests use the existing refrigerator prompt, 300-token cap,
  and seeds 0, 1, 2. These are separate from challenge timing.

Verified with the [model endpoints API](https://openrouter.ai/api/v1/models/google/gemma-4-26b-a4b-it/endpoints).
Routing follows [provider selection](https://openrouter.ai/docs/guides/routing/provider-selection)
and [reasoning controls](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens).

## Run

From the repository root, with Python 3.11 or newer (no third-party packages):

The saved OpenRouter runs used `bench/openrouter.py`, since merged into `bench/venue.py`, the client the Mac and
AWS runs use. `venue.py` keeps its safeguards: the key is read only from `OPENROUTER_API_KEY` or a dotenv file and is
never printed or saved, the provider is pinned with fallbacks off, and `--expect-provider` rejects any reply the API
reports as served by someone else.

```bash
python3 bench/venue.py --base-url https://openrouter.ai/api/v1 --model google/gemma-4-26b-a4b-it --venue openrouter --precision fp8 --server "OpenRouter, pinned to DeepInfra" --api-key-env OPENROUTER_API_KEY --env-file .env --expect-provider DeepInfra --extra '{"reasoning": {"enabled": false}, "provider": {"only": ["deepinfra/fp8"], "allow_fallbacks": false, "require_parameters": true, "quantizations": ["fp8"]}}' --results bench/results/openrouter-gemma4-26b-rerun.json
```

For Qwen, use `--model qwen/qwen3.8-27b --precision bf16` and `deepinfra/bf16` with `bf16` in the pin. Omit
`--env-file` when using an environment variable. `--mode all` performs its own smoke test, then 3 speed requests,
29 challenge requests and the five document sizes; `--contexts ""` skips the documents. Files are saved after
each completed request. Existing results are never overwritten: choose a new
filename for a new run. An error stops the run, marks it incomplete, and retains
completed answers. There are no hidden retries or provider substitutions.

At the endpoint's checked output price of $0.34 per million tokens, the
configured maximum output for one complete run costs approximately $0.061,
plus input tokens. Recheck current pricing in preflight before future runs.
Actual usage and provider-reported cost are retained in the result.
The price above is for Gemma. Qwen's checked output price is $1.875 per million
tokens, or approximately $0.336 at the full configured output cap plus input.
Its endpoint reported a nonzero health status when checked; the runner records
that metadata and requires the smoke test to pass before sending the quiz.

## Interpreting results

Results include exact request bodies, a prompt-set hash, timestamp, endpoint
metadata, provider response IDs, answers, finish reasons, usage, and streamed
text chunks with arrival times. Responses containing reasoning are rejected
because this comparison requires thinking off.

- Time to first text starts before the HTTP request and ends at the first
  nonempty visible text chunk. It includes network and queue time.
- Total request time includes the stream's completion, including usage metadata.
- Throughput is completion tokens divided by total request seconds. It is
  **not** Ollama's internal decode tokens/sec. Chunk count is never token count.
- Do not insert these values into the existing local speed chart. A comparison
  slide needs corresponding client measurements from the Mac and AWS.
- FP8/BF16 vs nvfp4 and different serving engines make this a deployment comparison,
  not an isolated hardware benchmark. Provider-reported metadata does not pin
  the hosted checkpoint revision or underlying GPU.

The local result files and speed chart remain separate. Slide 5 now shows the
hosted comparison. `python3 bench/publish_openrouter.py` regenerates its HTML
table, speaker notes and Markdown table from both saved runs; the normal
`bench/summarize.py` command calls it too.

## Verify offline

```bash
python3 -m pytest bench/test_venue.py
```

Tests cover visible-text timing, token usage, interrupted/error streams,
unexpected reasoning, credential-file parsing, the key header, provider rejection and cost totals.

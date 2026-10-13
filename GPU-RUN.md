# GPU run: the same tests on an L40S

One sitting on an AWS g6e.xlarge (1x NVIDIA L40S, 48 GB) in us-east-2, running the tests the Mac and OpenRouter already ran, so the deck can put three environments side by side. Resource IDs and the S3 layout are below.

Completed results and interpretation: [LANDING.md](LANDING.md#results). Raw result files retain all attempted and incomplete runs. The sections below retain the launch/run procedure for reproducibility.

## What gets measured

Every test is driven from the Mac by `bench/venue.py` through an SSH tunnel. Every venue gets the same requests and the same client clock, and the documents are cut from the Mac's own files, with a unique per-request prefix. The source corpus is intended to match, but no corpus hash was saved; byte identity across runs is not proven.

| Test | Same as | Recorded |
| :--- | :--- | :--- |
| Challenge, 29 questions | Mac `quiz.py --set challenge`, OpenRouter | Score, seconds per answer, cut-off answers |
| Speed, 3 short requests | OpenRouter, `bench/mac_client_speed.py` | Time to first text, completion tokens per total request second |
| Documents with target-size IDs 2K, 8K, 33K, 131K and 262K (not actual token counts) | Mac What fits slide (`speed.py --same-text`) | Wait before the first text, reading speed, or "too long" if the server refuses |
| Context that fits | Mac peak memory | vLLM's KV cache capacity at startup, and `nvidia-smi` |

Memory isn't compared directly. vLLM claims a fixed share of GPU memory up front, so per-document peaks don't exist the way they do on the Mac. On the L40S, "what fits" is the longest context vLLM can hold next to the weights. vLLM states that number when it starts.

Settings everywhere: temperature 0, seed 0, thinking off, 6,144-token answer cap. A cut-off answer counts as wrong.

| Model | Server | Thinking off |
| :--- | :--- | :--- |
| `Qwen/Qwen3.8-27B-FP8` | vLLM v0.32.0 | `{"chat_template_kwargs": {"enable_thinking": false}}` |
| `RedHatAI/gemma-4-26B-A4B-it-FP8-dynamic` | vLLM v0.32.0 | the same (Gemma's template already defaults it to off) |
| `RedHatAI/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-FP8` | vLLM v0.32.0 | the same |
| `rafw007/qwen3.8-27b-redteam` (Q4_K_M) | Ollama 0.40.6 | `{"reasoning_effort": "none"}` |

All three chat templates read `enable_thinking`: Qwen and Nemotron default it to on, and Gemma to off. `bench/venue.py` rejects any reply that still contains reasoning, so a wrong switch stops the run instead of skewing the results. If the v0.32.0 image fails on a model, retry it on v0.31.0 and record the version.

## Before launch

- **Rehearsed:** `bench/venue.py` ran end to end against Gemma 4 26B on the Mac's Ollama `/v1` (2026-10-24). Its document timings matched the overnight server timings: 3.4 s and 13.0 s against 3 s and 13 s. Its per-answer time matched within 0.3 s on the same questions. But the answers weren't identical to the overnight native-API run: Q11 ran to the token cap and Q28 flipped, so 26/29 against 27/29. Comparisons should use runs that went through the same path.
- **Mac baselines through `venue.py`:** these are scheduled in the overnight runner (step E in `~/.local/share/open-weights-bench/runner.sh`), using `venue-step.sh` beside it. They cover the same four models on the Mac's Ollama 0.40.6 `/v1`, so the Mac, L40S and OpenRouter rows share a client and request path. Questions and speed run at an 8,192-token default context, as the overnight quiz did. Documents run at a 262,144-token default context. Results go to `bench/results/mac-venue-*-qa.json` and `bench/results/mac-venue-*-docs.json`.
- **Your IP:** if your home IP changed, update the `open-weights-ssh` SSH rule with My IP.
- **AWS sign-in:** run `aws login --profile open-weights` if your session expired.

## AWS resources

Profile `open-weights`, account 717915633540, signed in with `aws login --profile open-weights`. Everything is in **us-east-2**, where the G and VT on-demand quota is 504 vCPUs (it is 0 in us-east-1). The profile defaults to us-east-1, so always pass `--region us-east-2`.

- **Key pair:** `open-weights` (ED25519), private key at `~/.ssh/open-weights.pem`.
- **Security group:** `sg-07eb55bfc5ed413db` (`open-weights-ssh`). SSH from the home IP only; vLLM and Ollama are reached through an SSH tunnel.
- **Bucket:** `open-weights-717915633540-us-east-2-an`, public access blocked, SSE-S3.
- **Role and instance profile:** `open-weights-ec2`, inline policy `open-weights-ec2Policy`, read and write on that bucket only.

S3 layout (uploaded from `~/hf-stage/` on the Mac):

```
models/Qwen/Qwen3.8-27B-FP8/017b9c7af6b5689d5dd426a76e0bc077eb5ca20a/                                  30.9 GB, 81 files
models/RedHatAI/gemma-4-26B-A4B-it-FP8-dynamic/ed35d7abe5d940da41b4ff06eb482feb0be8cb44/               28.7 GB, 17 files
models/RedHatAI/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-FP8/bff279eb543e15f7c0e3f922661e66a1b78ac2e0/    32.3 GB, 11 files
```

## Run

**1. Launch.** Launch a g6e.xlarge in the console with a 250 GiB gp3 disk, key `open-weights`, security group `open-weights-ssh` and instance profile `open-weights-ec2`, using AMI `ami-02c04e39084ed697f` (Deep Learning Base OSS Nvidia Driver GPU AMI, Ubuntu 24.04, built 2026-10-16, checked in us-east-2 on 2026-10-25). SSH in, then set a safety stop. The instance's shutdown behaviour is Stop, so this stops it after 5 hours even if you forget:

```bash
sudo shutdown -h +300
```

Record the hardware:

```bash
nvidia-smi
```

```bash
nvidia-smi -q > ~/nvidia-smi.txt
```

**2. Copy the models from S3.** Copy them to the instance disk, about 92 GB. The instance role grants read access to the bucket:

```bash
aws s3 sync s3://open-weights-717915633540-us-east-2-an/models /opt/models --region us-east-2
```

**3. Fit check, before any other test.** The Mac read 262,144-token documents with every model except Nemotron, which crashed. So the GPU has to hold the same window, or the comparison isn't like for like. Start each vLLM model with `--max-model-len 262144` (the command in step 5), read the KV cache line vLLM prints at startup, then stop it with `Ctrl-C`. That takes a few minutes per model, and no other test runs until all three pass.

What to expect: FP8 weights, plus attention memory at 262K in 16-bit, with vLLM allowed 92% of the card (about 44 GB). The attention figures are computed from each model's `config.json`. Only its full-attention layers grow with context.

| Model | Weights | Attention memory at 262K | Expected |
| :--- | ---: | ---: | :--- |
| Gemma 4 26B | 28.7 GB | 5.4 GB (5 full-attention layers) | Fits |
| Nemotron 3.5 Lightning | 32.3 GB | 1.6 GB (6 full-attention layers) | Fits |
| Qwen 3.8 27B | 30.9 GB | 17.2 GB (16 full-attention layers) | **Does not fit** |
| Redteam on Ollama, Q4_K_M | 16.6 GB | Mac peak at 262K was 36.1 GB | Fits |

The fit check is a result, not a gate. The L40S is the rented card closest to the Mac's roughly 56 GB GPU budget, and that's the comparison. Decided 2026-10-25: no bigger GPU, and no 8-bit attention memory, which would change the precision.

If a model doesn't fit 262K, as expected for Qwen:

1. Save the log with vLLM's message. It names the largest window that fits.
2. Restart that model with `--max-model-len` set to that length.
3. Run all of its tests. The documents above the limit come back as "too long", the same way the deck shows "over max" on the Mac.

**4. Open the tunnel.** On the Mac, in its own terminal, forward vLLM (port 8000) and Ollama (port 11434 on the instance, 11437 on the Mac):

```bash
ssh -i ~/.ssh/open-weights.pem -N -L 8000:127.0.0.1:8000 -L 11437:127.0.0.1:11434 ubuntu@<public-dns>
```

**5. Serve each vLLM model in turn.** One model at a time on the instance. Ask for the full 262,144-token window. If vLLM says the KV cache can't hold it, it prints the largest length that fits. Restart with that length and record it, because it's the L40S's "what fits" result:

```bash
sudo docker run -d --name vllm --gpus all -p 127.0.0.1:8000:8000 -v /opt/models:/models -v ~/.cache/vllm:/root/.cache/vllm vllm/vllm-openai:v0.32.0 --model /models/Qwen/Qwen3.8-27B-FP8/017b9c7af6b5689d5dd426a76e0bc077eb5ca20a --served-model-name qwen3.8-27b-fp8 --max-model-len 262144 --max-num-seqs 16 --gpu-memory-utilization 0.92
```

Follow it with `sudo docker logs -f vllm`. Before starting the next model, save the log and remove the container:

```bash
sudo docker logs vllm > ~/vllm-qwen.log 2>&1; sudo docker rm -f vllm
```

Then, on the Mac, run the tests:

```bash
python3 bench/venue.py --base-url http://127.0.0.1:8000/v1 --model qwen3.8-27b-fp8 --venue l40s-vllm --baseline qwen3.8:27b --precision fp8 --server "vLLM 0.32.0" --extra '{"chat_template_kwargs": {"enable_thinking": false}}' --results bench/results/l40s-qwen38-27b.json
```

Repeat for Gemma and Nemotron with their own paths from the S3 layout below, served names, `--baseline` tags (`gemma4:26b-nvfp4`, `nemotron-3.5-lightning:30b-a3b-mlx`) and results files. Copy each `vllm-*.log` back to `bench/results/` afterwards. The startup line with the KV cache size is the context-that-fits evidence.

**6. Redteam on Ollama.** Stop the last vLLM container first, so Ollama has the whole GPU. Install Ollama 0.40.6 for Linux. The install script pins the version through `OLLAMA_VERSION`:

```bash
curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.40.6 sh
```

The installer starts Ollama as a background service. Stop it, then start Ollama yourself with a full-size default context. Ollama's OpenAI endpoint can't set the context per request, and Ollama silently cuts prompts that don't fit:

```bash
sudo systemctl stop ollama
```

```bash
OLLAMA_CONTEXT_LENGTH=262144 ollama serve
```

Pull the model:

```bash
ollama pull rafw007/qwen3.8-27b-redteam
```

Check `ollama list`. The ID must be `c9195f0496d5`, the same file as on the Mac. The model's own settings cap its context at 65,536 tokens (`num_ctx 65536`), which overrides `OLLAMA_CONTEXT_LENGTH`, and the `/v1` endpoint can't change it per request. So for the documents, create the same 262K tag the Mac uses, over the same weights file:

```bash
printf 'FROM rafw007/qwen3.8-27b-redteam:latest\nPARAMETER num_ctx 262144\n' > Modelfile && ollama create qwen3.8-27b-redteam-262k -f Modelfile
```

Run the questions and speed on `rafw007/qwen3.8-27b-redteam:latest` and the documents on `qwen3.8-27b-redteam-262k:latest`, as the Mac did. Then, on the Mac:

```bash
python3 bench/venue.py --base-url http://127.0.0.1:11437/v1 --model rafw007/qwen3.8-27b-redteam:latest --venue l40s-ollama --baseline rafw007/qwen3.8-27b-redteam:latest --precision Q4_K_M --server "Ollama 0.40.6" --extra '{"reasoning_effort": "none"}' --results bench/results/l40s-qwen38-27b-redteam.json
```

**7. Stop.** Stop the instance in the console as soon as the last run finishes. Delete the instance and its disk once the results look right. The disk costs about $20 a month even while stopped.

## Time and cost (estimates, not measured)

Treat the following as planning estimates, not performance predictions. Memory bandwidth alone does not determine speed across different precision formats, engines and hardware. The actual L40S results are still pending.

| Phase | Estimate |
| :--- | :--- |
| Boot, S3 copy, vLLM image pull | 20 to 30 min |
| Qwen 3.8 27B FP8, all tests | 30 to 45 min |
| Gemma 4 26B FP8, all tests | 10 to 20 min |
| Nemotron 3.5 Lightning FP8, all tests | 10 to 20 min |
| Redteam on Ollama, all tests | 40 to 60 min |
| **Total** | **about 2 to 3 hours, about $4 to $6** |

Prices from the AWS price list for us-east-2, checked 2026-10-25: g6e.xlarge $1.861 an hour on demand, and gp3 storage $0.08 per GB-month. The 250 GiB disk is about $21 a month until you delete it.

## Learned on the first run (2026-10-25)

- **Run in the background.** `docker run -d --name vllm` keeps vLLM running when the SSH session ends. Piping a foreground container through `tee` lost the whole log when the container stopped.
- **`--max-num-seqs 16`.** By default vLLM prepares for 256 requests at once. Qwen 3.8 and Nemotron keep a fixed per-request state, and next to a long context only 185 of those slots fit, so startup fails. The tests send one request at a time, so 16 changes nothing in the results.
- **Keep the compile cache.** `-v ~/.cache/vllm:/root/.cache/vllm` saves the 69-second compile on every restart.
- **Startup takes about 10 minutes**, mostly reading weights from the gp3 disk at about 125 MB/s.
- **Qwen 3.8 27B fit result:** 262,144 tokens need 16.32 GiB of context memory, and 8.85 GiB is available, so the largest window is 139,552 tokens (`bench/results/l40s-fit-qwen38-27b-262k.log`).

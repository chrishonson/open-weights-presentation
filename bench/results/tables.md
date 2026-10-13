## Memory and waiting time

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

## Speed and accuracy

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

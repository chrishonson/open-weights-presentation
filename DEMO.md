# Live demo: the voice loop

Slide 11 of the deck ("Live demo"). The laptop answers spoken questions with ships-computer (`~/git/ships-computer`): Parakeet v3 speech to text, `gemma4:latest` in Ollama, Pocket TTS. Slide 10 shows the measured numbers, so if the demo fails the talk still makes its point.

The demo uses `demo/live-demo.toml`, not ships-computer's own `configs/live.toml`. Two differences:

1. **No coding agents.** `live.toml` lets the voice loop start `claude` or `agy` with every permission auto-approved in `~/git`. In a room, anyone's voice could trigger that. The demo config has no `[agents]` section and its system prompt does not mention tools.
2. **A stock voice.** `live.toml` clones a real person's voice (`voices/majel.wav`). The demo config uses Pocket TTS's `alba`. Change `[tts] voice` if you decide otherwise.

## The day before

1. Install and check the loop:

   ```bash
   cd ~/git/ships-computer && uv sync
   ```

2. Record a fresh scripted session with the demo config, so slide 10 shows current numbers. It plays about 40 seconds of audio through the speakers.

   ```bash
   cd ~/git/ships-computer && uv run python -m ships_computer.live --config ~/git/open-weights-presentation/demo/live-demo.toml --script configs/live-test.toml
   ```

3. Copy the newest `~/git/ships-computer/results/*-live.jsonl` into `bench/results/voice/`. In `bench/voice.json`, set `file`, `measured` and `ollama_version` (from `curl -s localhost:11434/api/version`). Then rebuild:

   ```bash
   OLLAMA_HOST=127.0.0.1:11436 python3 bench/summarize.py
   ```

4. Turn Wi-Fi off and run the live loop once. Everything it needs must already be on disk, and it is a good line for the talk.

## 30 minutes before

- AC power. Focus mode on, so no notifications come out of the speakers.
- The benchmark runner must not be loaded. This prints nothing when it is off:

  ```bash
  launchctl list | grep open-weights
  ```

- The Ollama app is running (the loop uses `localhost:11434`).
- Start the loop once, say "hello", stop it with `Ctrl-C`. This loads the models from disk so the first answer on stage is not slow.

The demo starts with wake-word gating off. Press `w` to toggle addressing it as “computer”; press `m` to mute or unmute the microphone.

## On stage

1. On slide 11, switch to Terminal and start the loop:

   ```bash
   cd ~/git/ships-computer && uv run python -m ships_computer.live --config ~/git/open-weights-presentation/demo/live-demo.toml
   ```

2. Wait for "Ship's computer online."
3. Ask one short question, for example "What is a fun fact about the moon?"
4. Ask a second one and interrupt it halfway: "Can you suggest a good opening line for a talk?" then "Actually, never mind."
5. Point at the terminal: each turn prints its voice-to-voice time.
6. `Ctrl-C` and go back to the deck.

## If it goes wrong

| Problem | Fix |
| :--- | :--- |
| It hears itself and keeps answering | Set `half_duplex = true` in `demo/live-demo.toml`. Interrupting stops working. |
| The room is too loud for the laptop mic | Use a headset mic, or skip to step 6 |
| Nothing happens within a few seconds | Stop, go back to slide 10. The measured numbers make the same point. |
| It cuts a sentence in two | It waits 300 ms of silence and checks Smart Turn v3 (up to 1.2 s for mid-thought pauses). Speak without pauses longer than 1.2 s. |

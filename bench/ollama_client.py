"""Minimal Ollama HTTP client shared by the speed and quiz benchmarks."""
import ctypes
import functools
import json
import os
import re
import subprocess
import threading
import urllib.request

# Same variable the ollama CLI reads, so a second Ollama version can run side by side on another port.
OLLAMA = os.environ.get("OLLAMA_HOST", "localhost:11434")
OLLAMA = OLLAMA if "://" in OLLAMA else "http://" + OLLAMA
NS = 1e9


def post(path, payload, timeout=4 * 3600, retries=2):
    """POST to Ollama. Retries HTTP 500, which Ollama 0.40's MLX runner returns when it crashes mid-reply."""
    req = urllib.request.Request(
        OLLAMA + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code != 500 or retries == 0:
            raise
        print(f"  HTTP 500 from Ollama, retrying ({retries} left)", flush=True)
        return post(path, payload, timeout, retries - 1)


def get(path):
    with urllib.request.urlopen(OLLAMA + path, timeout=30) as resp:
        return json.loads(resp.read())


def installed_models():
    return sorted(m["name"] for m in get("/api/tags")["models"])


def unload_all():
    for m in get("/api/ps")["models"]:
        post("/api/generate", {"model": m["name"], "keep_alive": 0})


@functools.lru_cache
def has_baked_system_prompt(model):
    """True if the model's Modelfile sets a SYSTEM prompt, as some community fine-tunes do."""
    return bool(post("/api/show", {"model": model}).get("system", "").strip())


def messages(prompt, baked_system):
    """Every model gets the same prompt: a baked-in system prompt is replaced by an empty one."""
    return ([{"role": "system", "content": ""}] if baked_system else []) + [{"role": "user", "content": prompt}]


def chat(model, prompt, num_predict, num_ctx=None, think=False, seed=0, temperature=0):
    options = {"temperature": temperature, "seed": seed, "num_predict": num_predict}
    if num_ctx:
        options["num_ctx"] = num_ctx
    return post(
        "/api/chat",
        {
            "model": model,
            "messages": messages(prompt, has_baked_system_prompt(model)),
            "stream": False,
            "think": think,
            "keep_alive": "30m",
            "options": options,
        },
    )


_LIBPROC = ctypes.CDLL("/usr/lib/libproc.dylib")


def runner_pid(model=None):
    """PID of the loaded model's runner process, or None if no runner is alive.

    Benchmarks unload everything first, so normally one runner is alive: `ollama runner` (MLX) or `llama-server`.
    Another app can still load a model meanwhile, so MLX runners named for a different model are skipped.
    """
    return find_runner(subprocess.run(["ps", "-axo", "pid,command"], capture_output=True, text=True).stdout, model)


def find_runner(ps_output, model=None):
    """PID of the runner in `ps -axo pid,command` output. llama-server can live in the app bundle or beside a
    standalone `ollama` binary, so it is matched by name wherever it is."""
    for line in ps_output.splitlines():
        pid, _, command = line.strip().partition(" ")
        exe = command.split(" ", 1)[0]
        if not (command.startswith(("ollama runner", "/")) and ("ollama runner" in command or exe.endswith("/llama-server"))):
            continue
        named = re.search(r"--model (\S+)", command)
        if model and named and not named.group(1).startswith("/") and named.group(1) != model:
            continue
        return int(pid)
    return None


def process_memory(pid):
    """(current, peak since the last reset_peak) bytes for a process, from the kernel's rusage_info_v4.

    macOS has two process measures and each misses something: footprint misses llama.cpp's memory-mapped
    weights, and resident size (RSS) misses MLX's GPU-only buffers. The larger of the two is right for both.
    """
    buf = (ctypes.c_uint64 * 40)()
    if _LIBPROC.proc_pid_rusage(pid, 4, buf) != 0:
        return None
    u = buf[2:]  # past the 16-byte uuid
    current = max(u[7], u[6])  # ri_phys_footprint, ri_resident_size
    return current, max(current, u[33])  # ri_interval_max_phys_footprint


def reset_peak(pid):
    """Start a new interval for the kernel's footprint peak, so loading the model is not counted."""
    _LIBPROC.proc_reset_footprint_interval(pid)


def runner_memory(model=None):
    """(current, peak) bytes used by the loaded model's runner process, or None if no runner is alive."""
    pid = runner_pid(model)
    return process_memory(pid) if pid else None


def runner_memory_gb(model=None):
    """Memory used by the loaded model's runner process right now, in GB."""
    mem = runner_memory(model)
    return round(mem[0] / 1e9, 2) if mem else None


class PeakMemory:
    """Highest memory of the model's runner while the `with` block runs, in GB (`.gb`).

    Resets the kernel's footprint peak on entry, so an already loaded model's loading spike is not counted,
    then samples every half second, so RSS growth (llama.cpp's weights) is seen while it happens. The kernel
    peak catches short footprint spikes between samples.
    """

    def __init__(self, model, interval=0.5):
        self.model, self.interval, self.peak = model, interval, 0
        self._stop = threading.Event()

    def _sample(self):
        mem = runner_memory(self.model)
        if mem:
            self.peak = max(self.peak, *mem)

    def _loop(self):
        while not self._stop.wait(self.interval):
            self._sample()

    def __enter__(self):
        if pid := runner_pid(self.model):
            reset_peak(pid)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        self._sample()

    @property
    def gb(self):
        return round(self.peak / 1e9, 2) if self.peak else None

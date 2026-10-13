"""bench/venue.py against a local fake OpenAI-compatible server that streams real SSE. Run: python3 -m pytest bench"""
import http.server
import json
import pathlib
import subprocess
import sys
import threading
import io
import os
import urllib.error
from unittest.mock import patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import venue  # noqa: E402
from quiz import grade_math  # noqa: E402

REQUESTS = []
HEADERS = []


class FakeServer(http.server.BaseHTTPRequestHandler):
    """Answers every chat request with 'OK' (or 'ANSWER: 4'), and refuses prompts longer than 20,000 characters."""

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        REQUESTS.append(body)
        HEADERS.append(dict(self.headers))
        prompt = body["messages"][0]["content"]
        if len(prompt) > 20000:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "maximum context length exceeded"}')
            return
        text = "OK" if "exactly OK" in prompt else "Work.\nANSWER: 4"
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for event in ({"choices": [{"delta": {"role": "assistant"}}]},
                      {"provider": "DeepInfra", "choices": [{"delta": {"content": text}}]},
                      {"choices": [{"delta": {}, "finish_reason": "stop"}]},
                      {"choices": [], "usage": {"prompt_tokens": len(prompt) // 4, "completion_tokens": 3, "cost": 0.001}}):
            self.wfile.write(f"data: {json.dumps(event)}\n\n".encode())
        self.wfile.write(b"data: [DONE]\n\n")

    def log_message(self, *args):
        pass


@pytest.fixture()
def server():
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakeServer)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    REQUESTS.clear()
    HEADERS.clear()
    yield f"http://127.0.0.1:{s.server_port}/v1"
    s.shutdown()


def test_payload_merges_the_thinking_off_fields():
    p = venue.payload("m", "hi", 10, seed=2, extra={"chat_template_kwargs": {"enable_thinking": False}})
    assert p["chat_template_kwargs"] == {"enable_thinking": False} and p["seed"] == 2 and p["temperature"] == 0 and p["stream"]


def test_a_reply_cut_off_at_the_cap_counts_as_wrong_even_if_it_grades_right():
    always_right = lambda text: (True, "ok")
    assert venue.grade({"finish_reason": "length", "response": "ANSWER: 4"}, always_right)["correct"] is False
    assert venue.grade({"finish_reason": "stop", "response": "ANSWER: 4"}, always_right)["correct"] is True


def test_documents_report_reading_speed_and_flag_a_refused_long_prompt(server):
    short = venue.read_document(server, "m", 2048)
    assert short["prompt_tokens"] > 0 and short["reading_tok_s"] > 0 and "too_long" not in short
    long = venue.read_document(server, "m", 32768)
    assert long["too_long"] is True and "HTTP 400" in long["error"]


def test_full_run_saves_every_part_and_never_overwrites(server, tmp_path):
    out = tmp_path / "run.json"
    cmd = [sys.executable, str(pathlib.Path(venue.__file__)), "--base-url", server, "--model", "m", "--venue", "fake",
           "--contexts", "2048,32768", "--extra", '{"reasoning_effort": "none"}', "--results", str(out)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(out.read_text())
    assert data["status"] == "complete" and len(data["questions"]) == 29 and len(data["speed_runs"]) == 3
    assert [d.get("too_long", False) for d in data["documents"]] == [False, True]
    assert data["summary"]["total"] == 29 and data["settings"]["extra"] == {"reasoning_effort": "none"}
    again = subprocess.run(cmd, capture_output=True, text=True)
    assert again.returncode != 0 and "already exists" in again.stderr


@pytest.mark.parametrize('code,message', [(400, b'unsupported parameter'), (500, b'server failed')])
def test_document_errors_are_not_reported_as_context_limits(code, message):
    error = urllib.error.HTTPError('http://localhost/test', code, 'failed', {}, io.BytesIO(message))
    with patch.object(venue, 'complete', side_effect=error), pytest.raises(RuntimeError, match='not a context-limit'):
        venue.read_document('http://localhost/v1', 'm', 2048)


def test_mac_speed_refuses_to_overwrite_saved_evidence(tmp_path):
    out = tmp_path / 'results.json'
    out.write_text('existing evidence')
    script = pathlib.Path(__file__).with_name('mac_client_speed.py')
    result = subprocess.run([sys.executable, str(script), '--results', str(out)], capture_output=True, text=True)
    assert result.returncode != 0 and 'already exists' in result.stderr
    assert out.read_text() == 'existing evidence'


def sse(data):
    return ("data: " + json.dumps(data) + "\n").encode()


def stream(reasoning=False, done=True, usage=True):
    rows = [b": keep-alive\n", sse({"choices": [{"delta": {"role": "assistant"}}]}),
            sse({"id": "gen-test", "provider": "DeepInfra", "choices": [{"delta": {"content": "ANSWER: 42"}}]})]
    if reasoning:
        rows.append(sse({"choices": [{"delta": {"reasoning": "thinking"}}]}))
    rows.append(sse({"choices": [{"delta": {}, "finish_reason": "stop"}]}))
    if usage:
        rows.append(sse({"choices": [], "usage": {"completion_tokens": 4}}))
    if done:
        rows.append(b"data: [DONE]\n")
    return rows


def test_timing_uses_visible_text_and_usage_not_chunk_count():
    times = iter([12.0, 14.0])
    r = venue.consume_stream(stream(), 10.0, lambda: next(times))
    assert r["time_to_first_text_s"] == 2 and r["seconds"] == 4 and r["completion_tokens_per_total_second"] == 1
    assert grade_math(r["response"], 42)[0]


@pytest.mark.parametrize("kwargs", [{"done": False}, {"usage": False}, {"reasoning": True}])
def test_incomplete_stream_missing_usage_and_reasoning_are_rejected(kwargs):
    with pytest.raises(RuntimeError):
        venue.consume_stream(stream(**kwargs), 0)


def test_a_stream_error_is_not_an_answer():
    with pytest.raises(RuntimeError):
        venue.consume_stream([sse({"error": {"message": "provider failure"}})], 0)


def test_env_file_is_parsed_not_executed(tmp_path):
    p = tmp_path / ".env"
    with patch.dict(os.environ, {}, clear=True):
        p.write_text('UNRELATED_SECRET=hidden\nexport OPENROUTER_API_KEY="fake-key"\n')
        assert venue.load_key("OPENROUTER_API_KEY", p) == "fake-key"
        p.write_text("OPENROUTER_API_KEY=$(false)\n")
        with pytest.raises(ValueError):
            venue.load_key("OPENROUTER_API_KEY", p)


def test_hosted_runs_send_the_key_check_the_provider_and_total_the_cost(server, tmp_path):
    env = tmp_path / ".env"
    env.write_text("TEST_KEY=fake-key\n")
    out = tmp_path / "run.json"
    base = [sys.executable, str(pathlib.Path(venue.__file__)), "--base-url", server, "--model", "m", "--venue", "hosted",
            "--mode", "smoke", "--api-key-env", "TEST_KEY", "--env-file", str(env)]
    subprocess.run(base + ["--expect-provider", "DeepInfra", "--results", str(out)], check=True, capture_output=True)
    assert HEADERS[0]["Authorization"] == "Bearer fake-key"
    assert json.loads(out.read_text())["summary"]["reported_cost_usd"] == 0.001
    wrong = subprocess.run(base + ["--expect-provider", "Elsewhere", "--results", str(tmp_path / "wrong.json")],
                           capture_output=True, text=True)
    assert wrong.returncode != 0 and "not 'Elsewhere'" in wrong.stderr


def test_local_runs_send_no_key_and_report_no_cost(server):
    venue.complete(server, venue.payload("m", "Reply with exactly OK.", 16))
    assert "Authorization" not in HEADERS[0]

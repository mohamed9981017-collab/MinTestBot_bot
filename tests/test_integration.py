"""End-to-end tests over real HTTP.

A real local HTTP server stands in for both the RSS feed and the Telegram Bot
API, so the production ``requests`` code paths are exercised without mocks.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from jobhunter.config import Config
from jobhunter.hunter import run_once

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>Jobs</title>
  <item>
    <title>Python Backend Engineer</title>
    <link>https://example.com/1</link>
    <guid>job-1</guid>
    <description><![CDATA[<p>Remote python role</p>]]></description>
    <pubDate>Mon, 29 Sep 2026 10:00:00 GMT</pubDate>
  </item>
  <item>
    <title>Senior Python Architect</title>
    <link>https://example.com/2</link>
    <guid>job-2</guid>
    <description>senior python role</description>
  </item>
  <item>
    <title>Graphic Designer</title>
    <link>https://example.com/3</link>
    <guid>job-3</guid>
    <description>figma</description>
  </item>
</channel></rss>
"""


class _Handler(BaseHTTPRequestHandler):
    received = []

    def log_message(self, *args):  # silence test output
        pass

    def do_GET(self):
        if self.path.startswith("/rss"):
            body = RSS.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/rss+xml")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        payload = json.loads(raw or b"{}")
        _Handler.received.append((self.path, payload))
        body = json.dumps({"ok": True, "result": {"message_id": len(_Handler.received)}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture()
def server():
    _Handler.received = []
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        thread.join(timeout=5)


def make_config(server, tmp_path, **overrides):
    values = {
        "TELEGRAM_TOKEN": "test-token",
        "TELEGRAM_CHAT_ID": "12345",
        "RSS_FEEDS": f"{server}/rss",
        "JOB_KEYWORDS": "python",
        "EXCLUDE_KEYWORDS": "senior",
        "STATE_FILE": str(tmp_path / "seen.json"),
        "TELEGRAM_API_BASE": server,
    }
    values.update(overrides)
    return Config.from_env(values)


def test_run_once_sends_only_matching_new_jobs(server, tmp_path):
    config = make_config(server, tmp_path)
    result = run_once(config)

    assert result.feeds_ok == 1
    assert result.entries == 3
    assert result.matched == 1  # senior excluded, designer not matched
    assert result.new == 1
    assert result.sent == 1

    assert len(_Handler.received) == 1
    path, payload = _Handler.received[0]
    assert path == "/bottest-token/sendMessage"
    assert payload["chat_id"] == "12345"
    assert payload["parse_mode"] == "HTML"
    assert "Python Backend Engineer" in payload["text"]


def test_run_once_is_idempotent(server, tmp_path):
    config = make_config(server, tmp_path)
    first = run_once(config)
    second = run_once(config)

    assert first.sent == 1
    assert second.new == 0
    assert second.sent == 0
    assert len(_Handler.received) == 1


def test_dry_run_does_not_send_or_mark_seen(server, tmp_path):
    config = make_config(server, tmp_path, DRY_RUN="true")
    result = run_once(config)

    assert result.sent == 1
    assert _Handler.received == []
    assert not (tmp_path / "seen.json").exists()


def test_broken_feed_does_not_abort_cycle(server, tmp_path):
    config = make_config(server, tmp_path, RSS_FEEDS=f"{server}/missing,{server}/rss")
    result = run_once(config)

    assert result.feeds_failed == 1
    assert result.feeds_ok == 1
    assert result.sent == 1

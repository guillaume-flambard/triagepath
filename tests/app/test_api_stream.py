"""triagepath — streaming API (SSE) tests.

WS1: verify the analysis graph streams incrementally as Server-Sent Events
(reasoning transparency), surfaces the human-review interrupt, and resumes via
``POST /api/review`` to produce the final report.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def _parse_sse(text: str) -> list[tuple[str, dict]]:
    """Parse an SSE body into [(event, data), ...]."""
    frames = []
    current_event = None
    current_data = []
    for line in text.splitlines():
        if line.startswith("event:"):
            current_event = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data.append(line.split(":", 1)[1].strip())
        elif line == "" and current_event is not None:
            frames.append((current_event, json.loads("\n".join(current_data))))
            current_event = None
            current_data = []
    if current_event is not None:
        frames.append((current_event, json.loads("\n".join(current_data))))
    return frames


def test_stream_runs_incrementally_and_interrupts():
    resp = client.post("/api/analyze/stream", json={"preset": "lumea", "llm_provider": "mock"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    frames = _parse_sse(resp.text)
    events = [e for e, _ in frames]

    # First frame must announce the thread.
    assert events[0] == "thread"
    assert frames[0][1]["thread_id"]

    # Node progress must stream through (reasoning transparency).
    node_events = [d["node"] for e, d in frames if e == "node"]
    assert "ingest" in node_events
    assert "score" in node_events
    assert "deep_dive" in node_events

    # The run must pause at the human-review interrupt, then end.
    assert "interrupt" in events
    assert "done" in events


def test_review_resumes_to_final_report():
    resp = client.post("/api/analyze/stream", json={"preset": "saas", "llm_provider": "mock"})
    thread_id = _parse_sse(resp.text)[0][1]["thread_id"]

    # Resume the paused thread (approve).
    rev = client.post("/api/review", json={"thread_id": thread_id, "action": "approve"})
    assert rev.status_code == 200
    body = rev.json()
    assert body["thread_id"] == thread_id
    assert "final" in body
    assert body["final"]  # non-empty final report

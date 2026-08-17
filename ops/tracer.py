"""triagepath — AgentOps tracing (WS6).

A lightweight, dependency-free run tracer. A ``Tracer`` records the execution
of a graph run: thread id, node/event steps with timing, and any LLM token
usage reported to it. Deterministic and offline (no external trace backend);
the trace is a plain dict you can persist anywhere.
"""

from __future__ import annotations

import time
import uuid


class Tracer:
    def __init__(self):
        self.run_id = None
        self.started_at = None
        self.finished_at = None
        self.steps: list[dict] = []
        self.token_usage: dict[str, int] = {}  # {"input": n, "output": n}

    def start(self, thread_id: str | None = None) -> str:
        self.run_id = thread_id or f"trace-{uuid.uuid4().hex[:12]}"
        self.started_at = time.time()
        self.steps = []
        self.token_usage = {}
        return self.run_id

    def step(self, node: str, message: str = "", *, kind: str = "node", extra: dict | None = None) -> None:
        self.steps.append(
            {
                "ts": round(time.time(), 3),
                "kind": kind,
                "node": node,
                "message": message,
                **(extra or {}),
            }
        )

    def add_tokens(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.token_usage["input"] = self.token_usage.get("input", 0) + input_tokens
        self.token_usage["output"] = self.token_usage.get("output", 0) + output_tokens

    def finish(self) -> None:
        self.finished_at = time.time()

    @property
    def duration_s(self) -> float:
        if self.started_at is None:
            return 0.0
        end = self.finished_at or time.time()
        return round(end - self.started_at, 3)

    def snapshot(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "duration_s": self.duration_s,
            "steps": self.steps,
            "token_usage": self.token_usage,
        }

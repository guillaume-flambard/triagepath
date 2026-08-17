"""triagepath — AgentOps versioned registry (WS6/8).

A simple, file-backed registry of agent definitions. Each entry pins the agent
id, a semantic version, the model, and the prompts used, so you can audit what
behaviour a given run was produced by and detect drift across versions.
Offline-safe: stored as JSON on disk (path configurable).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_REGISTRY = Path(os.environ.get("AGENT_REGISTRY", "agent_registry.json"))


class AgentRegistry:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else DEFAULT_REGISTRY
        self._data: dict = {}
        if self.path.exists():
            self._data = json.loads(self.path.read_text())

    def register(self, agent_id: str, version: str, model: str, prompts: dict, nodes: list[str]) -> dict:
        entry = {
            "agent_id": agent_id,
            "version": version,
            "model": model,
            "prompts": prompts,
            "nodes": nodes,
        }
        self._data.setdefault(agent_id, []).append(entry)
        self._persist()
        return entry

    def latest(self, agent_id: str) -> dict | None:
        versions = self._data.get(agent_id) or []
        return versions[-1] if versions else None

    def versions(self, agent_id: str) -> list[dict]:
        return self._data.get(agent_id) or []

    def all(self) -> dict:
        return self._data

    def _persist(self) -> None:
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2))

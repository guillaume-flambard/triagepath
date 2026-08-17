"""triagepath — AgentOps drift detection (WS6).

Flags behavioural drift between two versions of the graph/agents by comparing
their snapshots (node lists, prompt hashes, model names). Deterministic and
offline: two snapshots are "same" only when their structural fingerprint is
identical.
"""

from __future__ import annotations

import hashlib
import json


def fingerprint(snapshot: dict) -> str:
    """Stable hash of the structural parts of a snapshot (nodes + model + prompts)."""
    payload = {
        "nodes": snapshot.get("nodes", []),
        "model": snapshot.get("model", ""),
        "prompts": snapshot.get("prompts", {}),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def detect_drift(before: dict, after: dict) -> dict:
    """Compare two snapshots; return changed dimensions."""
    changes = {}
    for key in ("nodes", "model", "prompts"):
        a = before.get(key)
        b = after.get(key)
        if a != b:
            changes[key] = {"before": a, "after": b}
    return changes


def is_drifted(before: dict, after: dict) -> bool:
    return bool(detect_drift(before, after))

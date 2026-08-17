"""triagepath — AgentOps tests (WS6). All offline / deterministic."""

from __future__ import annotations

import os
import tempfile

from ops.cost import cost_of_run, estimate_cost
from ops.drift import detect_drift, fingerprint, is_drifted
from ops.registry import AgentRegistry
from ops.tracer import Tracer


def test_tracer_records_steps_tokens_duration():
    t = Tracer()
    t.start("run-x")
    t.step("ingest", "loaded")
    t.step("score", "scored")
    t.add_tokens(100, 20)
    t.finish()
    s = t.snapshot()
    assert [x["node"] for x in s["steps"]] == ["ingest", "score"]
    assert s["token_usage"] == {"input": 100, "output": 20}
    assert s["duration_s"] >= 0


def test_cost_mock_is_zero():
    assert estimate_cost("mock", 1000, 200) == 0.0
    assert estimate_cost("ollama", 1000, 200) == 0.0
    assert cost_of_run("mock", {"input": 500, "output": 50}) == 0.0


def test_cost_groq_scales_with_tokens():
    # 1M input tokens at groq rate -> ~0.59 USD
    assert estimate_cost("groq", 1_000_000, 0) == 0.59


def test_drift_detects_node_changes():
    a = {"nodes": ["ingest"], "model": "llama", "prompts": {"sys": "x"}}
    b = {"nodes": ["ingest", "score"], "model": "llama", "prompts": {"sys": "x"}}
    assert is_drifted(a, b)
    assert "nodes" in detect_drift(a, b)
    assert fingerprint(a) == fingerprint({"model": "llama", "prompts": {"sys": "x"}, "nodes": ["ingest"]})


def test_registry_versions_agents(tmp_path):
    reg = AgentRegistry(tmp_path / "reg.json")
    reg.register("copilot", "1.0.0", "llama", {"sys": "x"}, ["ingest"])
    reg.register("copilot", "1.1.0", "llama", {"sys": "y"}, ["ingest", "score"])
    assert reg.latest("copilot")["version"] == "1.1.0"
    assert [v["version"] for v in reg.versions("copilot")] == ["1.0.0", "1.1.0"]
    # persisted to disk
    assert (tmp_path / "reg.json").exists()

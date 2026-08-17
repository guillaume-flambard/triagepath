# triagepath — AgentOps (WS6/8)

Observability + versioning for the agentic copilot. Offline-first and
deterministic so the suite stays hermetic.

## Components

| Module | Role |
|---|---|
| `tracer.py` | Per-run execution trace (nodes, steps, timing, token usage) |
| `cost.py` | Token cost per provider (mock/ollama = 0, groq = per-1M rates) |
| `drift.py` | Compare snapshots to flag behavioural drift (nodes/model/prompts) |
| `registry.py` | File-backed versioned registry of agent definitions |

## Usage

```python
from ops.tracer import Tracer
from ops.cost import cost_of_run
from ops.drift import detect_drift, is_drifted
from ops.registry import AgentRegistry

# trace a run
t = Tracer()
t.start("run-123")
t.step("ingest", "loaded")
t.step("score", "scored 4 tasks")
t.add_tokens(1000, 200)
t.finish()
trace = t.snapshot()
print("cost (groq):", cost_of_run("groq", trace["token_usage"]))

# drift between two graph versions
if is_drifted(before_snapshot, after_snapshot):
    print("DRIFT:", detect_drift(before_snapshot, after_snapshot))

# versioned agent registry
reg = AgentRegistry("agent_registry.json")
reg.register("copilot", "1.0.0", "llama", {"system": "..."}, ["ingest", "score"])
print(reg.latest("copilot")["version"])
```

## Wiring into the graph

A `Tracer` can be driven from the LangGraph stream (one `t.step(...)` per
node event) and from the LLM client (report token usage via `t.add_tokens`).
The registry pins the exact model + prompts a run was produced by, which is what
makes drift detection meaningful across deployments.

## Tests

```bash
.venv/bin/python -m pytest tests/ops/
```

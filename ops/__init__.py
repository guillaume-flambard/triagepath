"""triagepath — AgentOps (WS6/8).

Observability + versioning for the agentic copilot:

- ``tracer``: record per-run execution traces (nodes, events, timing, token usage).
- ``cost``: estimate token cost per provider (mock = 0, ollama = 0, groq = per-token rates).
- ``drift``: compare two graph snapshots / prompt sets to flag behavioural drift.
- ``registry``: versioned registry of agent definitions (id, version, model, prompts).

All components are offline-first and deterministic so the suite stays hermetic.
"""

"""triagepath — AgentOps token cost (WS6).

Estimates the financial cost of a run from its token usage, per provider.
Offline-safe: ``mock`` and ``ollama`` cost nothing; ``groq`` uses public
per-1M-token rates. Rates are deliberately simple and configurable.
"""

from __future__ import annotations

# Per-1M-token USD rates (approx, public pricing).
RATES: dict[str, dict[str, float]] = {
    "mock": {"input": 0.0, "output": 0.0},
    "ollama": {"input": 0.0, "output": 0.0},
    "groq": {"input": 0.59, "output": 0.79},  # llama-3.3-70b class
}


def estimate_cost(provider: str, input_tokens: int, output_tokens: int) -> float:
    """Return USD cost for the given token usage under ``provider``."""
    r = RATES.get(provider, RATES["groq"])
    return round((input_tokens / 1e6) * r["input"] + (output_tokens / 1e6) * r["output"], 6)


def cost_of_run(provider: str, token_usage: dict) -> float:
    """Convenience: cost from a Tracer token_usage dict."""
    return estimate_cost(provider, token_usage.get("input", 0), token_usage.get("output", 0))

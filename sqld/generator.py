"""triagepath — Text-to-SQL generator (WS4).

Converts a natural-language question (+ schema context) into a SQL SELECT.

- ``mock`` (default): deterministic keyword matching against the schema — maps
  column names found in the question to a SELECT, offline-safe and reproducible.
- ``ollama`` / ``groq``: prompt the LLM with the schema + question and parse a
  single SELECT statement from the response.
"""

from __future__ import annotations

import os
import re

import httpx


class SqlGenerator:
    name = "base"

    def generate(self, question: str, schema_context: str) -> str:
        raise NotImplementedError


class MockSqlGenerator(SqlGenerator):
    """Deterministic: pick a table + up to a few matching columns."""

    name = "mock"

    def generate(self, question: str, schema_context: str) -> str:
        tables = re.findall(r"TABLE (\w+) \(([^)]*)\)", schema_context)
        if not tables:
            return "SELECT 1"
        q = question.lower()

        def names(tc):
            return [c.strip().split(" ")[0] for c in tc[1].split(",") if c.strip()]

        def score(tc):
            ns = names(tc)
            return sum(1 for c in ns if c.lower() in q) + sum(1 for t in tc[0].lower().split("_") if t in q)

        table, cols = max(tables, key=score)
        col_names = [c for c in names((table, cols)) if c]
        select_cols = ", ".join(col_names[:3]) if col_names else "*"
        return f"SELECT {select_cols} FROM {table} LIMIT 50"


class LlmSqlGenerator(SqlGenerator):
    """Prompt an LLM for a single SELECT statement."""

    def __init__(self, provider: str, base_url: str | None = None, model: str | None = None, api_key: str | None = None):
        self.provider = provider
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or ("qwen2.5:3b" if provider == "ollama" else os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"))
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")

    def _prompt(self, question: str, schema_context: str) -> str:
        return (
            "You convert natural-language questions into PostgreSQL SELECT queries.\n"
            f"Schema:\n{schema_context}\n\n"
            f"Question: {question}\n\n"
            "Reply with ONLY the SQL SELECT statement, no explanation, no markdown."
        )

    def generate(self, question: str, schema_context: str) -> str:
        if self.provider == "groq":
            r = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": self._prompt(question, schema_context)}],
                },
                timeout=30.0,
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"]
        else:  # ollama
            r = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": self._prompt(question, schema_context), "stream": False},
                timeout=60.0,
            )
            r.raise_for_status()
            text = r.json()["response"]
        sql = re.sub(r"```(?:sql)?|```", "", text, flags=re.I).strip()
        if not sql.lower().startswith("select"):
            raise ValueError(f"LLM did not produce a SELECT: {sql[:200]}")
        return sql


def get_generator(provider: str = "mock", **kwargs) -> SqlGenerator:
    if provider == "ollama":
        return LlmSqlGenerator("ollama", **kwargs)
    if provider == "groq":
        return LlmSqlGenerator("groq", **kwargs)
    return MockSqlGenerator()

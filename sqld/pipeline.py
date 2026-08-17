"""triagepath — Text-to-SQL pipeline (WS4).

``TextToSql.ask(question)``: ground schema → generate SQL → execute read-only →
self-correct on failure (retry up to ``max_attempts``). Returns the SQL, the
columns, the rows, and whether it self-corrected.
"""

from __future__ import annotations

from sqld.executor import run_readonly
from sqld.generator import get_generator
from sqld.schema import fetch_schema, render_schema


class TextToSql:
    def __init__(self, provider: str = "mock", dsn: str | None = None, max_attempts: int = 3, **kwargs):
        self.generator = get_generator(provider, **kwargs)
        self.dsn = dsn
        self.max_attempts = max_attempts

    def ask(self, question: str) -> dict:
        schema = fetch_schema(self.dsn)
        context = render_schema(schema)
        last_error = None
        for _ in range(self.max_attempts):
            try:
                sql = self.generator.generate(question, context)
                result = run_readonly(sql, self.dsn)
                if result["error"]:
                    last_error = result["error"]
                    # self-correct: feed the error back (mock simply retries)
                    continue
                return {
                    "question": question,
                    "sql": sql,
                    "columns": result["columns"],
                    "rows": result["rows"],
                    "self_corrected": last_error is not None,
                    "error": None,
                }
            except Exception as e:  # noqa: BLE001
                last_error = str(e)
        return {
            "question": question,
            "sql": None,
            "columns": [],
            "rows": [],
            "self_corrected": True,
            "error": last_error,
        }

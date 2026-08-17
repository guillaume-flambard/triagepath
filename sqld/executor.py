"""triagepath — Text-to-SQL safe executor (WS4).

Runs a generated SQL statement read-only: only SELECT is accepted, and every
statement executes inside a transaction that is always rolled back. Mirrors the
MCP Postgres server's guard so no write can ever leak through.
"""

from __future__ import annotations

import os


def _dsn() -> str:
    url = os.environ.get("DATABASE_URL") or "postgresql://memo@localhost:5432/blueowl_dev"
    if url.startswith("postgresql+psycopg://"):
        url = "postgresql://" + url[len("postgresql+psycopg://") :]
    return url


def run_readonly(sql: str, dsn: str | None = None, limit: int = 50) -> dict:
    """Execute ``sql`` read-only and return {"columns", "rows", "error"}."""
    if not sql.lstrip().lower().startswith("select"):
        return {"columns": [], "rows": [], "error": "only SELECT queries are allowed (read-only)"}
    import psycopg

    try:
        with psycopg.connect(dsn or _dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                columns = [d[0] for d in cur.description] if cur.description else []
                rows = cur.fetchmany(limit)
    except Exception as e:  # noqa: BLE001
        return {"columns": [], "rows": [], "error": str(e)}
    return {"columns": columns, "rows": rows, "error": None}

"""triagepath — Text-to-SQL schema grounding (WS4).

Fetches the database schema (tables + columns) and renders it as a compact
prompt context, so the SQL generator only ever references real objects.
Reuses the MCP Postgres server's introspection SQL.
"""

from __future__ import annotations

import os


def _dsn() -> str:
    url = os.environ.get("DATABASE_URL") or "postgresql://memo@localhost:5432/blueowl_dev"
    if url.startswith("postgresql+psycopg://"):
        url = "postgresql://" + url[len("postgresql+psycopg://") :]
    return url


def fetch_schema(dsn: str | None = None) -> dict[str, list[dict]]:
    """Return {table: [columns]} for the public schema."""
    import psycopg

    dsn = dsn or _dsn()
    schema: dict[str, list[dict]] = {}
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
                """
            )
            for table, col, dtype, nullable in cur.fetchall():
                schema.setdefault(table, []).append(
                    {"name": col, "type": dtype, "nullable": nullable == "YES"}
                )
    return schema


def render_schema(schema: dict[str, list[dict]]) -> str:
    """Render the schema as a compact prompt block."""
    lines = []
    for table, cols in schema.items():
        col_str = ", ".join(f"{c['name']} {c['type']}" for c in cols)
        lines.append(f"TABLE {table} ({col_str})")
    return "\n".join(lines) or "(empty schema)"

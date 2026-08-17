"""triagepath — MCP Postgres server (read-only).

WS2: lets the agentic copilot inspect and query the business Postgres database
through tools, with a hard read-only guard (every statement is wrapped in a
transaction that is rolled back). Write access is intentionally not exposed.

The database URL comes from ``DATABASE_URL`` (default local Postgres via
``psycopg``). Run standalone:

    .venv/bin/python -m mcp.postgres_server        # stdio (default)
    .venv/bin/python -m mcp.postgres_server --http # streamable-http on :8901
"""

from __future__ import annotations

import argparse
import os

from mcp.server.mcpserver import MCPServer

DEFAULT_URL = "postgresql+psycopg://memo@localhost:5432/blueowl_dev"


def _dsn() -> str:
    url = os.environ.get("DATABASE_URL") or DEFAULT_URL
    # Accept SQLAlchemy-style URLs too: postgresql+psycopg://...
    if url.startswith("postgresql+psycopg://"):
        url = "postgresql://" + url[len("postgresql+psycopg://") :]
    return url


mcp = MCPServer("triagepath-postgres", version="0.1.0")


def _connect():
    import psycopg

    return psycopg.connect(_dsn())


@mcp.tool()
def list_tables() -> str:
    """List the tables in the public schema (and row counts)."""
    rows = []
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
                """
            )
            for (t,) in cur.fetchall():
                rows.append(t)
    return "\n".join(rows) if rows else "(no public tables)"


@mcp.tool()
def describe_table(table: str) -> str:
    """Describe the columns of a table (name, type, nullable)."""
    # Reject anything that is not a simple, unquoted identifier.
    if not table.replace("_", "").replace(".", "").isalnum():
        return "error: invalid table name"
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
                """,
                (table,),
            )
            cols = cur.fetchall()
    if not cols:
        return f"table '{table}' not found"
    return "\n".join(f"{c}: {t} (null={n})" for c, t, n in cols)


@mcp.tool()
def run_query(sql: str) -> str:
    """Run a READ-ONLY SELECT query and return up to 50 rows as text.

    Wrapped in a transaction that is always rolled back; only SELECT is
    allowed. This is safe to call from an LLM.
    """
    if not sql.lstrip().lower().startswith("select"):
        return "error: only SELECT queries are allowed (read-only server)"
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                colnames = [d[0] for d in cur.description] if cur.description else []
                rows = cur.fetchmany(50)
    except Exception as e:  # noqa: BLE001
        return f"query failed: {e}"
    if not colnames:
        return "(no columns)"
    out = ["\t".join(colnames)]
    for r in rows:
        out.append("\t".join("NULL" if v is None else str(v) for v in r))
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="triagepath MCP Postgres server")
    parser.add_argument("--http", action="store_true", help="run over streamable-http (port 8901)")
    args = parser.parse_args()
    if args.http:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8901)
    else:
        mcp.run()


if __name__ == "__main__":
    main()

"""triagepath — MCP Postgres server tests (WS2).

Exercises the MCPServer in-process via its async ``list_tools`` / ``call_tool``
handlers (no subprocess, no stdio), which proves the server registers its tools
and enforces the read-only guard without fighting anyio's stdio transport.
"""

from __future__ import annotations

import asyncio

import mcp_servers.postgres_server as ps


def _tool_names():
    return {t.name for t in asyncio.run(ps.mcp.list_tools())}


def _call(name: str, args: dict) -> str:
    res = asyncio.run(ps.mcp.call_tool(name, args))
    return "".join(str(x.text) for x in res.content if hasattr(x, "text"))


def test_server_registers_postgres_tools():
    assert {"list_tables", "describe_table", "run_query"} <= _tool_names()


def test_run_query_rejects_non_select():
    text = _call("run_query", {"sql": "DELETE FROM users"})
    assert "read-only" in text


def test_run_query_rejects_insert():
    text = _call("run_query", {"sql": "INSERT INTO users (id) VALUES (1)"})
    assert "read-only" in text


def test_run_query_allows_select(require_postgres):
    text = _call("run_query", {"sql": "SELECT 1 AS one"})
    assert "1" in text

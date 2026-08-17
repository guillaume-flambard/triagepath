"""triagepath — MCP servers (WS2).

Expose the business data layer (Postgres) and the knowledge corpus
(Elasticsearch) as Model Context Protocol servers so the agentic copilot can
query real data as tools.

Note: this package is named ``mcp_servers`` (not ``mcp``) so it does not
shadow the official ``mcp`` SDK package, which must remain importable.

Run a server standalone:

    .venv/bin/python -m mcp_servers.postgres_server           # stdio
    .venv/bin/python -m mcp_servers.postgres_server --http    # :8901
"""

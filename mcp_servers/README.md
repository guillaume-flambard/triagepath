# triagepath — MCP servers (WS2)

Expose the business data layer to the agentic copilot as Model Context
Protocol servers, so it can query real data as tools instead of hard-coding
access.

> **Naming note:** this package is `mcp_servers`, **not** `mcp`, so it never
> shadows the official `mcp` SDK package that must stay importable.

## Servers

| Server | Tools | Backend |
|---|---|---|
| `postgres_server.py` | `list_tables`, `describe_table`, `run_query` (read-only) | Postgres via `psycopg` |
| `elasticsearch_server.py` | `list_indices`, `search` | Elasticsearch via HTTP (`httpx`) |

## Run

```bash
# stdio transport (default) — for a local MCP client / agent
.venv/bin/python -m mcp_servers.postgres_server
.venv/bin/python -m mcp_servers.elasticsearch_server

# network transport (streamable-http)
.venv/bin/python -m mcp_servers.postgres_server --http        # :8901
.venv/bin/python -m mcp_servers.elasticsearch_server --http    # :8902
```

## Configuration

- **Postgres**: `DATABASE_URL` (SQLAlchemy or `postgresql://` URL). Read-only is
  enforced in `run_query`: only `SELECT` is accepted, every statement runs in a
  transaction that is rolled back. Write tools are intentionally absent.
- **Elasticsearch**: `ES_URL` (default `http://localhost:9200`). Search-only;
  indexing is owned by the RAG pipeline (WS3/5).

## Wire into a client

```python
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession

params = StdioServerParameters(command=".venv/bin/python",
                               args=["-m", "mcp_servers.postgres_server"])
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        tools = await session.list_tools()
        res = await session.call_tool("run_query", {"sql": "SELECT 1"})
```

## Tests

```bash
.venv/bin/python -m pytest tests/mcp/
```

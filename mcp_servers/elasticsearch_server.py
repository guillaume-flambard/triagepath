"""triagepath — MCP Elasticsearch server (search-only).

WS2: lets the agentic copilot search the knowledge corpus indexed in
Elasticsearch. Exposes read-only search + index-listing tools; indexing is
handled by the RAG pipeline (WS3/5), not by this server.

Connection via ``ES_URL`` (default http://localhost:9200). Uses plain HTTP
(httpx) so no extra client dependency is needed. Run standalone:

    .venv/bin/python -m mcp_servers.elasticsearch_server           # stdio
    .venv/bin/python -m mcp_servers.elasticsearch_server --http    # :8902
"""

from __future__ import annotations

import argparse
import json
import os

import httpx
from mcp.server.mcpserver import MCPServer

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")

mcp = MCPServer("triagepath-elasticsearch", version="0.1.0")


def _client() -> httpx.Client:
    return httpx.Client(base_url=ES_URL, timeout=10.0)


@mcp.tool()
def list_indices() -> str:
    """List the Elasticsearch indices and their document counts."""
    try:
        with _client() as c:
            r = c.get("/_cat/indices?v=true&h=index,docs.count")
            r.raise_for_status()
        return r.text.strip() or "(no indices)"
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"


@mcp.tool()
def search(index: str, query: str, size: int = 5) -> str:
    """Full-text search a single index for ``query``, returning up to ``size`` hits."""
    try:
        body = {"query": {"multi_match": {"query": query, "fields": ["*"]}}, "size": size}
        with _client() as c:
            r = c.post(f"/{index}/_search", json=body)
            r.raise_for_status()
            data = r.json()
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"
    hits = data.get("hits", {}).get("hits", [])
    if not hits:
        return "(no hits)"
    out = []
    for h in hits:
        src = h.get("_source", {})
        # Keep the snippet short and flat.
        text = json.dumps(src, ensure_ascii=False, default=str)[:500]
        out.append(f"[{h.get('_score', '')}] {text}")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="triagepath MCP Elasticsearch server")
    parser.add_argument("--http", action="store_true", help="run over streamable-http (port 8902)")
    args = parser.parse_args()
    if args.http:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8902)
    else:
        mcp.run()


if __name__ == "__main__":
    main()

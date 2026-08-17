"""triagepath — RAG vector stores (WS3/5).

A minimal vector-store interface with two backends:

- ``MemoryVectorStore`` (default): in-memory cosine-similarity search. Offline,
  deterministic, ideal for demos and tests.
- ``PgVectorStore``: pgvector-backed search over a ``vector`` column in the
  configured Postgres. Used when the extension is available.

Elasticsearch hybrid/re-rank lives in the Elasticsearch MCP server (WS2) and is
composed at the retrieval layer; this module owns the dense-vector path.
"""

from __future__ import annotations

import math


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class MemoryVectorStore:
    """In-memory store: (id, vector, metadata). Cosine similarity search."""

    def __init__(self):
        self._items: list[dict] = []

    def add(self, vector: list[float], text: str, metadata: dict | None = None) -> str:
        vid = f"v{len(self._items)}"
        self._items.append({"id": vid, "vector": vector, "text": text, "metadata": metadata or {}})
        return vid

    def add_many(self, vectors: list[list[float]], texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        ids = []
        for i, v in enumerate(vectors):
            meta = metadatas[i] if metadatas else {}
            ids.append(self.add(v, texts[i], meta))
        return ids

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        scored = sorted(
            (
                {"id": it["id"], "text": it["text"], "metadata": it["metadata"], "score": _cosine(vector, it["vector"])}
                for it in self._items
            ),
            key=lambda d: d["score"],
            reverse=True,
        )
        return scored[:top_k]

    def count(self) -> int:
        return len(self._items)


class PgVectorStore:
    """pgvector-backed store over a table ``rag_chunks`` (id, embedding, text, source)."""

    def __init__(self, dsn: str, dim: int = 64):
        self.dsn = dsn
        self.dim = dim

    def _connect(self):
        import psycopg

        return psycopg.connect(self.dsn)

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rag_chunks (
                        id BIGSERIAL PRIMARY KEY,
                        embedding vector(%s),
                        text TEXT NOT NULL,
                        source TEXT NOT NULL DEFAULT ''
                    )
                    """,
                    (self.dim,),
                )

    def add_many(self, vectors: list[list[float]], texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                for i, v in enumerate(vectors):
                    src = (metadatas[i] if metadatas else {}).get("source", "")
                    cur.execute(
                        "INSERT INTO rag_chunks (embedding, text, source) VALUES (%s, %s, %s) RETURNING id",
                        (v, texts[i], src),
                    )
        return []

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, text, source, embedding <=> %s AS distance
                    FROM rag_chunks ORDER BY embedding <=> %s LIMIT %s
                    """,
                    (vector, vector, top_k),
                )
                rows = cur.fetchall()
        return [{"id": str(r[0]), "text": r[1], "metadata": {"source": r[2]}, "score": 1.0 - float(r[3])} for r in rows]


def get_store(kind: str = "memory", **kwargs) -> object:
    """Build a vector store by name (memory | pgvector)."""
    if kind == "pgvector":
        store = PgVectorStore(**kwargs)
        store.ensure_schema()
        return store
    return MemoryVectorStore()

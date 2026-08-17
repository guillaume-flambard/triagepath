"""triagepath — RAG pipeline orchestration (WS3).

``ingest`` chunks + embeds + stores documents; ``retrieve`` embeds a query and
returns the top-k chunks. Composes the pluggable embedding provider and vector
store from :mod:`rag.embeddings` and :mod:`rag.stores`.
"""

from __future__ import annotations

from rag.chunking import chunk_document
from rag.embeddings import get_embeddings
from rag.stores import get_store


class RagPipeline:
    def __init__(self, provider: str = "mock", store_kind: str = "memory", **kwargs):
        self.embeddings = get_embeddings(provider, **kwargs)
        self.store = get_store(store_kind, **kwargs)

    def ingest_document(self, doc: dict) -> int:
        """Chunk + embed + store a ``{"content", "source"}`` doc. Returns chunk count."""
        chunks = chunk_document(doc)
        if not chunks:
            return 0
        vectors = self.embeddings.embed_many([c["text"] for c in chunks])
        self.store.add_many(vectors, [c["text"] for c in chunks], [{"source": c["source"]} for c in chunks])
        return len(chunks)

    def ingest_documents(self, docs: list[dict]) -> int:
        return sum(self.ingest_document(d) for d in docs)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        vec = self.embeddings.embed(query)
        return self.store.search(vec, top_k=top_k)

    def count(self) -> int:
        c = getattr(self.store, "count", None)
        return c() if c else 0

"""triagepath — RAG pipeline tests (WS3). All offline (mock embeddings/store)."""

from __future__ import annotations

from rag.chunking import chunk_text
from rag.embeddings import MockEmbeddingProvider
from rag.pipeline import RagPipeline


def test_chunk_text_small_doc_is_single_chunk():
    chunks = chunk_text("hello world", max_chars=800)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "hello world"


def test_chunk_text_splits_long_doc():
    text = "word " * 500  # ~2500 chars
    chunks = chunk_text(text, max_chars=200, overlap_chars=20)
    assert len(chunks) > 1
    # every chunk within max size
    assert all(len(c["text"]) <= 200 for c in chunks)
    # consecutive sources are indexed
    assert all(c["index"] == i for i, c in enumerate(chunks))


def test_mock_embedding_is_deterministic_and_normalized():
    emb = MockEmbeddingProvider()
    a = emb.embed("shopify order processing")
    b = emb.embed("shopify order processing")
    assert a == b  # deterministic
    norm = sum(x * x for x in a) ** 0.5
    assert abs(norm - 1.0) < 1e-6  # unit norm
    assert len(a) == MockEmbeddingProvider.dim


def test_mock_embedding_distinguishes_topics():
    emb = MockEmbeddingProvider()
    v_shopify = emb.embed("shopify orders shipping")
    v_email = emb.embed("email support tickets")
    v_similar = emb.embed("shopify order fulfillment")
    from rag.stores import _cosine

    assert _cosine(v_shopify, v_similar) > _cosine(v_shopify, v_email)


def test_pipeline_ingest_and_retrieve():
    pipe = RagPipeline(provider="mock", store_kind="memory")
    pipe.ingest_documents(
        [
            {"content": "Shopify order processing takes 3 minutes per order, highly repetitive.", "source": "a.md"},
            {"content": "Email support tickets take 10 minutes each, low repetitiveness.", "source": "b.md"},
        ]
    )
    assert pipe.count() == 2
    hits = pipe.retrieve("how long does shopify order processing take", top_k=1)
    assert hits
    assert "shopify" in hits[0]["text"].lower()

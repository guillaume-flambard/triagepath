"""triagepath — RAG embeddings (WS3).

Pluggable embedding provider, mirroring the project's LLM pattern:

- ``mock`` (default): deterministic bag-of-words hashing into a fixed-size
  vector. Zero network, offline-safe, stable across runs (same text → same
  vector) so retrieval is reproducible in demos and tests.
- ``ollama``: local embeddings via ``POST /api/embeddings`` (requires a model).
- ``groq``: embeddings via the Groq API (requires a key).

All providers return a plain ``list[float]`` so the vector store is agnostic.
"""

from __future__ import annotations

import hashlib
import math
import os

import httpx


class EmbeddingProvider:
    """Thin interface; subclasses implement ``embed``."""

    name = "base"

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic hashed bag-of-words vectors (offline, reproducible)."""

    name = "mock"
    dim = 64

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in text.lower().split():
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 32) & 1 else -1.0
            vec[idx] += sign
        # Normalize.
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Local embeddings via Ollama's /api/embeddings endpoint."""

    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str = "nomic-embed-text"):
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model

    def embed(self, text: str) -> list[float]:
        r = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()["embedding"]


class GroqEmbeddingProvider(EmbeddingProvider):
    """Groq embeddings (needs GROQ_API_KEY + a Groq embedding model)."""

    name = "groq"

    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model = model

    def embed(self, text: str) -> list[float]:
        r = httpx.post(
            "https://api.groq.com/openai/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": text},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()["data"][0]["embedding"]


def get_embeddings(provider: str = "mock", **kwargs) -> EmbeddingProvider:
    """Build an embedding provider by name (mock | ollama | groq)."""
    p = provider or "mock"
    if p == "ollama":
        return OllamaEmbeddingProvider(**kwargs)
    if p == "groq":
        return GroqEmbeddingProvider(**kwargs)
    return MockEmbeddingProvider()

"""triagepath — RAG pipeline (WS3/5).

Ingest business docs → chunk → embed → store (vector), then retrieve relevant
snippets for the knowledge copilot. Embeddings and vector store are pluggable:

- **embeddings**: ``mock`` (deterministic, offline — default), ``ollama``, ``groq``
- **store**: ``memory`` (offline demo, default), ``pgvector``, ``elasticsearch``

This mirrors the project's LLM pattern (mock by default so the whole thing runs
offline for demos, real providers opt-in).
"""

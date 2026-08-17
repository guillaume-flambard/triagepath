# triagepath — RAG pipeline (WS3/5)

Ingest business docs → chunk → embed → store, then retrieve relevant snippets
for the knowledge copilot. Mirrors the project's LLM pattern: **mock by
default** (offline, deterministic, demo-ready), real providers opt-in.

## Components

| Module | Role |
|---|---|
| `chunking.py` | Split docs into retrieval-sized chunks (max size + overlap) |
| `embeddings.py` | Pluggable embeddings: `mock` (default), `ollama`, `groq` |
| `stores.py` | Vector stores: `memory` (default), `pgvector` |
| `pipeline.py` | `RagPipeline`: `ingest_documents` → `retrieve` |

## Usage

```python
from rag.pipeline import RagPipeline

pipe = RagPipeline(provider="mock", store_kind="memory")
pipe.ingest_documents([
    {"content": "Shopify orders take 3 min each, highly repetitive.", "source": "ops-notes.md"},
    # ...
])
hits = pipe.retrieve("how much time does shopify order processing take", top_k=3)
for h in hits:
    print(h["score"], h["text"])
```

## Providers & stores

- **Embeddings**: `mock` (deterministic hashed bag-of-words, offline),
  `ollama` (local `/api/embeddings`), `groq` (API key).
- **Stores**: `memory` (in-memory cosine, offline), `pgvector` (Postgres
  `vector` extension — requires the extension installed for your PG version).

### pgvector

```bash
# Postgres must have the vector extension for the matching version, then:
.venv/bin/python -c "
from rag.pipeline import RagPipeline
pipe = RagPipeline(provider='mock', store_kind='pgvector', dsn='postgresql://memo@localhost:5432/<db>')
pipe.ingest_documents([{'content':'...','source':'...'}])
"
```

Elasticsearch hybrid / re-rank is served by the ES MCP server (`mcp_servers/`).

## Tests

```bash
.venv/bin/python -m pytest tests/rag/
```

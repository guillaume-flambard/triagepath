"""triagepath — RAG chunking (WS3).

Splits documents into retrieval-sized chunks with optional overlap. Kept simple
and deterministic (no external dependency): split on paragraph/line boundaries
first, then enforce a max size by sliding windows.
"""

from __future__ import annotations

import re


def chunk_text(
    text: str,
    max_chars: int = 800,
    overlap_chars: int = 80,
    *,
    source: str = "",
) -> list[dict]:
    """Split ``text`` into chunks of ~``max_chars`` with ``overlap_chars``.

    Returns a list of ``{"text", "source", "index"}`` records.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [{"text": text, "source": source, "index": 0}]

    chunks: list[dict] = []
    start = 0
    i = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        # Prefer a sentence/space boundary just under the limit.
        if end < len(text):
            boundary = text.rfind(" ", start + max_chars // 2, end)
            if boundary > start:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "source": source, "index": i})
            i += 1
        if end >= len(text):
            break
        start = max(end - overlap_chars, start + 1)
    return chunks


def chunk_document(doc: dict, **kwargs) -> list[dict]:
    """Chunk a ``{"content", "source"}`` document."""
    return chunk_text(doc.get("content", ""), source=doc.get("source", ""), **kwargs)

"""triagepath — Text-to-SQL (WS4).

Turn a natural-language question into a safe, schema-grounded SQL query:
1. **ground** the schema (tables + columns) so the LLM only references real objects;
2. **generate** the SQL from the question + schema (mock/ollama/groq);
3. **execute** it read-only (SELECT-only, rolled back);
4. **self-correct** on failure (retry with the error message).

``mock`` generates deterministic SQL by matching keywords to known columns, so
the whole pipeline runs offline for demos and tests; live providers are opt-in.
"""

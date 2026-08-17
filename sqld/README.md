# triagepath — Text-to-SQL (WS4)

Turn a natural-language question into a safe, schema-grounded SQL query over the
business Postgres database.

## Pipeline

1. **Ground** the schema (`schema.py`): fetch tables + columns, render a compact prompt block.
2. **Generate** the SQL (`generator.py`): `mock` (default, deterministic keyword matching), `ollama`, `groq`.
3. **Execute** read-only (`executor.py`): only `SELECT`, wrapped in a rolled-back transaction.
4. **Self-correct** (`pipeline.py`): retry up to `max_attempts` feeding the error back.

## Usage

```python
from sqld.pipeline import TextToSql

r = TextToSql(provider="mock").ask("show me the users table")
print(r["sql"])       # SELECT ...
print(r["columns"])   # column names
print(r["rows"])      # rows (read-only)
print(r["error"])     # None on success
```

## Safety

`executor.run_readonly` rejects anything that isn't `SELECT` and rolls back the
transaction, so no write can ever reach the database from the copilot. The same
guard is enforced by the MCP Postgres server (`mcp_servers/`).

## Tests

```bash
.venv/bin/python -m pytest tests/sqld/
```

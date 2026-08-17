"""triagepath — Text-to-SQL tests (WS4). Uses mock generator against local Postgres."""

from __future__ import annotations

import pytest

from sqld.executor import run_readonly
from sqld.generator import MockSqlGenerator
from sqld.pipeline import TextToSql
from sqld.schema import fetch_schema, render_schema

PG_DSN = "postgresql://memo@localhost:5432/blueowl_dev"


@pytest.fixture(autouse=True)
def _pg_env(monkeypatch):
    # Other tests mutate DATABASE_URL (e.g. to sqlite); force Postgres so the
    # sqld suite is hermetic.
    monkeypatch.setenv("DATABASE_URL", PG_DSN)


def test_executor_rejects_non_select():
    assert "read-only" in run_readonly("DELETE FROM users")["error"]
    assert "read-only" in run_readonly("INSERT INTO users (id) VALUES (1)")["error"]


def test_mock_generator_emits_valid_select():
    schema = fetch_schema()
    context = render_schema(schema)
    sql = MockSqlGenerator().generate("show users", context)
    assert sql.lstrip().lower().startswith("select")


def test_pipeline_returns_select_and_rows():
    r = TextToSql(provider="mock").ask("show me the users table")
    assert r["error"] is None
    assert r["sql"].lower().startswith("select")
    assert isinstance(r["columns"], list)
    assert isinstance(r["rows"], list)


def test_render_schema_is_compact():
    schema = fetch_schema()
    text = render_schema(schema)
    assert text.startswith("TABLE ")
    assert "users" in text.lower()


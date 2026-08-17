"""Global test environment (loaded by pytest before any test module).

Guarantees the whole suite stays hermetic: the config settings singleton is
built once, at first project import, so these env vars must be in place before
any test module imports ``config``/``db``/``ui``. Otherwise a local ``.env``
with a live GROQ key would leak real LLM calls into the tests (and silently
consume the daily token quota until the rate limit breaks them).
"""

import os

import pytest

os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")


@pytest.fixture(scope="session")
def require_postgres():
    """Skip tests that need a real local Postgres (unavailable in CI)."""
    # Use an explicit local DSN, NOT DATABASE_URL, which other suites pollute
    # (e.g. to sqlite) at module import time.
    dsn = "postgresql://memo@localhost:5432/blueowl_dev"
    try:
        import psycopg

        with psycopg.connect(dsn):
            pass
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"local Postgres unavailable: {e}")
    return True

"""
PostgreSQL-specific tests for src/db.py.

These tests only run when DATABASE_URL is set to a PostgreSQL connection string.
If DATABASE_URL isn't set (or points to SQLite), the tests are skipped.

Why this exists:
    SQLite and PostgreSQL share ~90% of their SQL syntax, but they differ in
    subtle ways that only appear in production:

    - Placeholder syntax: '?' (SQLite) vs '%s' (PostgreSQL)
    - Aliases in HAVING: allowed (SQLite) vs forbidden (PostgreSQL)
    - Auto-increment: AUTOINCREMENT (SQLite) vs SERIAL (PostgreSQL)
    - Date formatting: strftime (SQLite) vs TO_CHAR (PostgreSQL)
    - Duplicate handling: INSERT OR IGNORE vs ON CONFLICT DO NOTHING

    These tests exercise the PostgreSQL path so we catch dialect bugs BEFORE
    they reach production.

How to run locally:
    # Get the External Database URL from Render:
    # dashboard.render.com → smart-log-analyzer-db → Info → Connections → External
    # Append ?sslmode=require to the end

    export DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
    pytest tests/test_db_postgres.py -v
    unset DATABASE_URL
"""

import os

import pytest

# Skip all tests in this file if DATABASE_URL isn't PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_POSTGRES = DATABASE_URL.startswith("postgres")

pytestmark = pytest.mark.skipif(
    not IS_POSTGRES,
    reason="PostgreSQL tests require DATABASE_URL to point to a PostgreSQL instance",
)


@pytest.fixture(scope="module")
def db_ready():
    """Ensure the table exists before running any tests."""
    from src.db import create_table

    create_table()
    yield
    # No teardown — we don't want to drop the table in production-like DBs


# =================== TABLE CREATION ===================


def test_create_table_idempotent(db_ready):
    """create_table() can be called multiple times safely."""
    from src.db import create_table

    create_table()
    create_table()
    # Should not raise


# =================== QUERY TESTS ===================


def test_query_top_ips_returns_list(db_ready):
    """query_top_ips returns a list (even if empty)."""
    from src.db import query_top_ips

    result = query_top_ips(limit=5)
    assert isinstance(result, list)


def test_query_top_ips_respects_limit(db_ready):
    """query_top_ips respects the limit parameter."""
    from src.db import query_top_ips

    result = query_top_ips(limit=2)
    assert len(result) <= 2


def test_query_top_ips_with_zero_limit(db_ready):
    """query_top_ips handles limit=0 without crashing."""
    from src.db import query_top_ips

    result = query_top_ips(limit=0)
    assert result == []


def test_query_hourly_volume_returns_list(db_ready):
    """query_hourly_volume returns a list."""
    from src.db import query_hourly_volume

    result = query_hourly_volume()
    assert isinstance(result, list)


def test_query_error_rate_returns_list(db_ready):
    """query_error_rate returns a list.

    This test specifically exercises the HAVING clause that broke in CI
    when it used an alias instead of an inline expression.
    """
    from src.db import query_error_rate

    result = query_error_rate()
    assert isinstance(result, list)


# =================== INSERT TESTS ===================


def test_insert_logs_returns_int(db_ready):
    """insert_logs returns an integer (count of inserted rows)."""
    from src.db import insert_logs

    # Empty insert should return 0
    result = insert_logs([])
    assert isinstance(result, int)
    assert result == 0


def test_insert_logs_skips_duplicates(db_ready):
    """insert_logs skips duplicates via ON CONFLICT DO NOTHING."""
    from datetime import datetime, timezone

    from src.db import get_connection, insert_logs

    # Build a unique log entry
    log = {
        "ip": "test-postgres-1.2.3.4",
        "timestamp_utc": datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        "timestamp_local": datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        "timezone_offset": "+0000",
        "method": "POST",
        "url": "/test-postgres-endpoint",
        "status": 200,
        "size": 1234,
    }

    # Cleanup: remove if exists (idempotent test)
    conn = get_connection()
    cursor = conn.cursor()
    (
        cursor.execute(
            "DELETE FROM logs WHERE ip = ?",
            ("test-postgres-1.2.3.4",),
        )
        if not IS_POSTGRES
        else cursor.execute(
            "DELETE FROM logs WHERE ip = %s",
            ("test-postgres-1.2.3.4",),
        )
    )
    conn.commit()
    conn.close()

    # First insert
    first = insert_logs([log])
    assert first == 1

    # Second insert — should be skipped
    second = insert_logs([log])
    assert second == 0

    # Cleanup
    conn = get_connection()
    cursor = conn.cursor()
    if IS_POSTGRES:
        cursor.execute("DELETE FROM logs WHERE ip = %s", ("test-postgres-1.2.3.4",))
    else:
        cursor.execute("DELETE FROM logs WHERE ip = ?", ("test-postgres-1.2.3.4",))
    conn.commit()
    conn.close()


# =================== DIALECT-SPECIFIC TESTS ===================


def test_placeholder_syntax_is_correct(db_ready):
    """Ensure query_top_ips uses the correct placeholder for PostgreSQL.

    This test catches the exact bug that broke production:
        'the query has 0 placeholders but 1 parameters were passed'
    """
    from src.db import query_top_ips

    # If the placeholder is wrong, this will raise psycopg.ProgrammingError
    # If it's correct, it returns a list
    result = query_top_ips(limit=10)
    assert isinstance(result, list)


def test_having_clause_works(db_ready):
    """Ensure query_error_rate's HAVING clause works on PostgreSQL.

    This test catches the 'HAVING error_count' bug — the alias-in-HAVING
    problem that SQLite allows but PostgreSQL forbids.
    """
    from src.db import query_error_rate

    result = query_error_rate()
    assert isinstance(result, list)


def test_date_formatting_works(db_ready):
    """Ensure query_hourly_volume uses the correct date function.

    SQLite uses strftime(); PostgreSQL uses TO_CHAR().
    If the wrong function is used, PostgreSQL raises an error.
    """
    from src.db import query_hourly_volume

    result = query_hourly_volume()
    assert isinstance(result, list)

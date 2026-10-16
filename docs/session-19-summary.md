# 📘 SESSION 19 SUMMARY — The SQL Dialect Bug

**Date:** 2026-10-15  
**Stage:** Production Debugging  
**Status:** ✅ RESOLVED

---

## 🐛 THE BUG

**Symptom:** The `/top-ips` endpoint returned HTTP 500 in production.

**What users saw:** The Streamlit dashboard displayed:
```
⚠️ API is waking up. Render's free tier sleeps after 15 minutes of inactivity.
This first request can take up to 60 seconds. Please refresh this page in a moment to try again.
```

**Why this message was misleading:** The dashboard's retry logic treats every non-200 response as "API is asleep." In reality, the API was fully up — but the `/top-ips` endpoint was crashing.

---

## 🔍 THE INVESTIGATION PATH

### Step 1: Confirm the API was actually awake

```bash
curl -s https://smart-log-analyzer-gl1x.onrender.com/health
# Output: {"status":"ok"}
```

**Result:** The API is awake. The problem is specific to one endpoint.

### Step 2: Test each endpoint from the browser

| Endpoint | Result |
|----------|--------|
| `/` | ✅ Welcome JSON |
| `/health` | ✅ `{"status":"ok"}` |
| `/top-ips` | ❌ **`Internal Server Error`** |
| `/hourly-volume` | ✅ Works |
| `/error-rates` | ✅ Works |

**Result:** Only `/top-ips` fails. This narrows the problem to one function.

### Step 3: Read the Render logs

**Path:** Render dashboard → `smart-log-analyzer` → **Logs**

**The exact error:**

```
File "/app/src/db.py", line 136, in query_top_ips
    cursor.execute(...)
psycopg.ProgrammingError: the query has 0 placeholders but 1 parameters were passed
```

**Result:** Placeholder mismatch. **This is the bug.**

---

## 🎯 ROOT CAUSE

**SQLite and PostgreSQL use different placeholder syntax:**

| Database | Placeholder |
|----------|-------------|
| **SQLite** | `?` |
| **PostgreSQL** | `%s` |

**The buggy code:**

```python
cursor.execute(
    """
    SELECT ip, COUNT(*) as request_count
    FROM logs
    GROUP BY ip
    ORDER BY request_count DESC
    LIMIT ?
    """,
    (limit,),
)
```

**What happens in PostgreSQL:**
- PostgreSQL sees `LIMIT ?` — the `?` is a **literal character**, not a placeholder
- The query has **0 placeholders** in PostgreSQL's eyes
- But 1 parameter (`limit`) is being passed
- **PostgreSQL throws:** `the query has 0 placeholders but 1 parameters were passed`

**Why it worked locally:**
- SQLite accepts `?` as its placeholder syntax
- SQLite is forgiving
- SQLite silently matches the `?` to the `(limit,)` parameter

**Why it broke in production:**
- PostgreSQL is strict about placeholder syntax
- PostgreSQL rejects the query when the parameter count doesn't match

---

## 🔧 THE FIX

**Replace the hardcoded `?` with a dynamic placeholder:**

```python
def query_top_ips(limit: int = 5) -> List[Dict]:
    """Get the top IPs by request count."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"
    cursor.execute(
        f"""
        SELECT ip, COUNT(*) as request_count
        FROM logs
        GROUP BY ip
        ORDER BY request_count DESC
        LIMIT {placeholder}
        """,
        (limit,),
    )
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results
```

**What changed:**

| Before | After |
|--------|-------|
| `LIMIT ?` (hardcoded) | `LIMIT {placeholder}` (dynamic) |
| Plain string `"""..."""` | F-string `f"""..."""` |
| No placeholder variable | `placeholder = "%s" if USE_POSTGRES else "?"` |

---

## 🎯 THE THREE SQL DIALECT BUGS WE'VE HIT

This was the **third** SQLite vs PostgreSQL bug. All three share a pattern:

| # | Bug | Trigger | Fix |
|---|-----|---------|-----|
| 1 | `HAVING error_count` alias | PostgreSQL forbids aliases in HAVING | Inline the SUM expression |
| 2 | `LIMIT ?` hardcoded | PostgreSQL doesn't understand `?` | Use dynamic placeholder |
| 3 | `UploadFile` typo | Case sensitivity in Python | Fix the case (capital F) |

**Every one was found by reading the Render logs.** Not by guessing.

---

## 🎯 THE LESSON — THE PATTERN

**Every query that works locally must be tested against the production database dialect.**

| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| Placeholder | `?` | `%s` |
| Auto-increment PK | `AUTOINCREMENT` | `SERIAL` |
| Duplicate handling | `INSERT OR IGNORE` | `ON CONFLICT DO NOTHING` |
| Date formatting | `strftime()` | `TO_CHAR()` |
| Aliases in HAVING | ✅ Allowed | ❌ Forbidden |
| Parameter mismatch | Silently ignored | Raised as error |

**PostgreSQL is strict. SQLite is forgiving. Write for the strict one.**

---

## 🎯 THE HARDENING — POSTGRESQL TESTS

**To prevent this class of bug forever, we added `tests/test_db_postgres.py`:**

- 11 tests that exercise the PostgreSQL code path
- Automatically skipped when `DATABASE_URL` isn't set
- Runs when `DATABASE_URL` points to PostgreSQL

**Tests cover:**
- Table creation idempotence
- All three query functions return lists
- Duplicate handling via `ON CONFLICT DO NOTHING`
- Placeholder syntax correctness
- HAVING clause without alias
- Date formatting

**Run locally:**
```bash
export DATABASE_URL="postgresql://...?sslmode=require"
pytest tests/test_db_postgres.py -v
unset DATABASE_URL
```

---

## 🎯 THE FINAL COMMITS

| Commit | Purpose |
|--------|---------|
| `b833a6c` | Fix the placeholder bug in `query_top_ips` |
| `cb6d0f7` | Format `db.py` with `black` after the fix |
| `c05c742` | Add PostgreSQL-specific tests |
| `e465570` | Add PostgreSQL service to CI to run the tests |

**Current status:**
- ✅ `/top-ips` returns real JSON
- ✅ Streamlit dashboard loads
- ✅ CI is green with 14 tests
- ✅ Dialect bugs are now permanently guarded

---

## 📝 MASTER'S NOTE

> *"The dialect bug that cost us hours was one character: `?` vs `%s`. But the fix wasn't just changing the character. The fix was: (1) read the Render logs, (2) understand the difference between SQLite and PostgreSQL, (3) write tests that catch this pattern forever. The forge teaches by making you debug. Then it teaches you to prevent."*

**End of Session 19.**

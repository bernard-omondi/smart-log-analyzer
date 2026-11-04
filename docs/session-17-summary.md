# 📘 SESSION 17 SUMMARY – SQL Dialect Bug Hunt

**Date:** 2026-10-09
**Stage:** Debugging PostgreSQL vs SQLite
**Status:** ⏸ PAUSED — Fix Pushed, Verifying Later

## The Bug
Streamlit Cloud dashboard returned:
"Could not connect to API. Error: Expecting value: line 1 column 1 (char 0)"

## The Investigation
1. Verified URL was correct (`gl1x` — with digit 1)
2. Verified Streamlit Secrets were correct
3. Added debug output to see the actual response
4. Debug showed: `500 Internal Server Error`
5. Checked Render logs → found the real error:
   `psycopg.errors.UndefinedColumn: column "error_count" does not exist`
   at `HAVING error_count > 0`

## Root Cause
**SQLite allows aliases in HAVING clauses. PostgreSQL does not.**
The `query_error_rate()` function in `src/db.py` used:
```sql
HAVING error_count > 0

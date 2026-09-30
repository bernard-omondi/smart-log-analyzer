# 📘 SESSION 14 SUMMARY – PostgreSQL Migration Complete

**Date:** 2026-09-26
**Commit:** a10b077
**Stage:** Production Persistence
**Status:** ✅ COMPLETED

## What We Achieved
- ✅ Migrated from SQLite to PostgreSQL
- ✅ Dual-engine architecture (SQLite for local, PostgreSQL for cloud)
- ✅ Database persists across container restarts
- ✅ 106 insertions, 67 deletions across 2 files
- ✅ All changes reviewed with `git diff` before commit

## The Architecture

USE_POSTGRES = DATABASE_URL is set and starts with "postgres"
│
├─ True → psycopg2 → PostgreSQL (cloud/production)
│ ├── SERIAL PRIMARY KEY
│ ├── %s placeholders
│ ├── ON CONFLICT DO NOTHING
│ └── TO_CHAR() for dates
│
└─ False → sqlite3 → SQLite (local development)
├── INTEGER AUTOINCREMENT
├── ? placeholders
├── INSERT OR IGNORE
└── strftime() for dates


## The Bugs We Fought Through
1. **`TabError`** — mix of tabs and spaces from pasting code → fixed with `expand -t 4`
2. **`near "%" syntax error`** — `get_connection()` didn't branch on `USE_POSTGRES`
3. **`KeyError: 0`** — PostgreSQL returns dicts, not tuples → access by column name
4. **Paste corruption** — chat rendering corrupted indentation → switched to `sed` + Python scripts

## The Migration Edits
| Edit | File | What |
|------|------|------|
| 1 | db.py | Added `import os` + `USE_POSTGRES` detection |
| 2 | db.py | Rewrote `get_connection()` to branch |
| 3 | db.py | Rewrote `create_table()` for SERIAL/AUTOINCREMENT |
| 4 | db.py | Rewrote `insert_logs()` for `%s`/`?` + ON CONFLICT/IGNORE |
| 5 | db.py | Rewrote `query_hourly_volume()` for TO_CHAR/strftime |
| 6 | ingest.py | Aliased queries → dict access, not tuple |

## Key Lessons
1. **Trust the connection, not the variable** — `USE_POSTGRES` can be `True` while `get_connection()` still connects to SQLite
2. **PostgreSQL uses %s, SQLite uses ?** — different placeholders
3. **PostgreSQL returns dicts, SQLite returns tuples** — access by name
4. **`expand -t 4` ends the tab war** — always run after pasting code
5. **`sed` + Python scripts beat nano** — scripting avoids paste corruption
6. **`git diff --stat` is faster than `git diff`** — for quick reviews
7. **`git diff` opens `less`** — press `q` to exit, `Space` to page down

## Render Configuration
- `DATABASE_URL` set to **Internal Database URL**
- PostgreSQL database: `smart-log-analyzer-db` (Free tier, Frankfurt)
- Auto-deploys on push

## Master's Note
> *"You now build with two engines. Local dev uses SQLite for speed; production uses PostgreSQL for persistence. The environment variable is your switch. Very few Python developers reach this milestone."*

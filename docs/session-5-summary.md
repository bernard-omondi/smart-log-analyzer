# 📘 SUMMARY – SESSION 5

Date: 2026-08-11  
Apprentice: Bernard Omondi  
Stage: Week 1 – Core Python Mastery (Database Integration)  
Status: ✅ COMPLETED

---

## 1. THE FOUR PILLARS OF YOUR LOG PIPELINE

| File | Role | Analogy |
|------|------|---------|
| `parser.py` | Parsing – Convert raw text → structured dictionaries | **The Translator** |
| `db.py` | Storage – Create tables, insert data, run queries | **The Librarian** |
| `ingest.py` | Orchestration – Control the pipeline from start to finish | **The Conductor** |
| `logs.db` | Data – The actual SQLite database file | **The Archive** |

---

## 2. WHAT WE ACCOMPLISHED

- ✅ Created `src/db.py` with SQLite integration
- ✅ Added indexes for performance (IP, timestamp, status)
- ✅ Implemented analytical queries (Top IPs, Hourly Volume, Error Rate)
- ✅ Created `src/ingest.py` to connect parser to database
- ✅ Fixed import errors with proper module imports
- ✅ Ran complete pipeline: logs → parser → database → queries

---

## 3. FILES CREATED

| File | Purpose |
|------|---------|
| `src/db.py` | Database functions (create, insert, query) |
| `src/ingest.py` | Pipeline orchestration (parse + insert) |
| `logs.db` | SQLite database file (ignored by git) |

---

## 4. IMPORT FIX (For Future Reference)

**Problem:** `ModuleNotFoundError: No module named 'parser'`

**Fix:**

```python
# Instead of:
from parser import read_logs

# Use:
from src.parser import read_logs
from src.db import insert_logs

```

## 📘 THE FOUR PILLARS OF YOUR LOG PIPELINE

| File | Role | Analogy | Key Functions | Knows About | Knows NOT About |
|---|---|---|---|---|---|
| `parser.py` | **Parsing** – Convert raw text → structured dictionaries | **The Translator** | `parse_line()`, `read_logs()` | Regex, datetime, log format | Database, CLI, orchestration |
| `db.py` | **Storage** – Create tables, insert data, run queries | **The Librarian** | `create_table()`, `insert_logs()`, `query_top_ips()`, `query_hourly_volume()`, `query_error_rate()` | SQLite, indexes, schema | Log format, parsing, orchestration |
| `ingest.py` | **Orchestration** – Control the pipeline from start to finish | **The Conductor** | `ingest_logs()` | The whole pipeline (parser + db + summary) | Implementation details of parsing or storage |
| `logs.db` | **Data** – The actual SQLite database file | **The Archive** | *(Not code – a file)* | Raw inserted data, query results | Code logic, parsing, orchestration |

---

1. parser.py – THE TRANSLATOR

What it does:

    Takes a raw log file (sample.log)

    Reads it line by line

    Converts each line into a Python dictionary using regex

Using this code:
python

def parse_line(line: str) -> dict:
    # Regex → extract IP, timestamp, method, URL, status, size

def read_logs(filepath: str):
    # Opens file, yields parsed dicts

What it returns:
python

{
    'ip': '127.0.0.1',
    'timestamp_utc': datetime(2000, 10, 10, 20, 55, 36),
    'timestamp_local': datetime(2000, 10, 10, 13, 55, 36),
    'timezone_offset': '-0700',
    'method': 'GET',
    'url': '/apache_pb.gif',
    'status': 200,
    'size': 2326
}

Why it exists:

    Parsing is complex (regex, timezone handling).

    You want to test and change parsing logic without touching database code.

    You can reuse it for CSV, JSON, or streaming logs later.

2. db.py – THE LIBRARIAN

What it does:

    Creates the database and table

    Inserts parsed dictionaries into logs.db

    Runs queries (Top IPs, hourly volume, error rates)

Code you wrote:
python

def create_table():
    # CREATE TABLE IF NOT EXISTS logs (...)

def insert_logs(logs: List[dict]) -> int:
    # INSERT INTO logs (...) VALUES (...)

def query_top_ips():
    # SELECT ip, COUNT(*) ... GROUP BY ip

def query_hourly_volume():
    # SELECT strftime(...), COUNT(*) ... GROUP BY hour

def query_error_rate():
    # SELECT url, error_rate ... WHERE status >= 500

Why it exists:

    Database operations are repetitive.

    You want to reuse insert/query logic in other scripts (e.g., a web API, reports).

    You can swap SQLite for PostgreSQL later by only changing db.py.

3. ingest.py – THE CONDUCTOR

What it does:

    Orchestrates the entire pipeline:

        Calls create_table() → ensures database exists

        Calls read_logs() → parses the log file

        Calls insert_logs() → stores the data

        Shows a summary (total rows, date range)

Code you wrote:
python

def ingest_logs(filepath: str):
    create_table()                    # Step 0: Prepare DB
    logs = list(read_logs(filepath))  # Step 1: Parse
    rows = insert_logs(logs)          # Step 2: Insert
    # Step 3: Summary
    print(f"✅ Inserted {rows} logs")

Why it exists:

    You want a single entry point for the pipeline.

    It keeps orchestration separate from parsing and storage.

    You can create other orchestrators (e.g., ingest_s3.py, ingest_kafka.py) that reuse parser.py and db.py.

4. logs.db – THE ARCHIVE

What it is:

    The actual SQLite database file on disk.

    Contains the logs table with all inserted rows.

Why it exists:

    Persistent storage – your data survives after the script ends.

    Queryable with SQL – you can run analytical queries directly.

How to inspect it:
bash

sqlite3 logs.db
.tables
SELECT * FROM logs;

## COMPARISON TABLE (At a Glance)

| Question | `parser.py` | `db.py` | `ingest.py` | `logs.db` |
|---|---|---|---|---|
| **Who reads raw logs?** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Who defines the schema?** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Who inserts data?** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Who orchestrates?** | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Who stores the data?** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Can I test it alone?** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ N/A |
| **Can I reuse it?** | ✅ Yes | ✅ Yes | ✅ Partially | ✅ N/A |


A FINAL MENTAL MODEL
text

📄 sample.log (raw text)
       ↓
🔍 parser.py → turns lines into dictionaries
       ↓
📦 list of dicts (structured data)
       ↓
📂 db.py → inserts into SQLite
       ↓
🗄️ logs.db (the actual database)
       ↓
📊 ingest.py → runs queries and shows summary
       ↓
📈 Top IPs, Hourly Volume, Error Rates


FINAL NOTE

    "parser.py translates. db.py stores. ingest.py conducts. logs.db remembers."



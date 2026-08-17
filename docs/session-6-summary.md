# PART 1: MASTER SUMMARY – OPTIONS 1–4 (The Scaling Journey)

# 📘 MASTER'S SUMMARY – OPTIONS 1–4 (The Scaling & Polish Phase)

Date: 2026-08-12 to 2026-08-14

Apprentice: Bernard Omondi

Stage: Week 2 – Scaling, Quality, CLI, & Visualization

Status: ✅ COMPLETED

1. WHAT WE ACCOMPLISHED

| Option | Description | Status |
|--------|-------------|--------|
| Option 3 | Scaled to 10,000+ log lines |	✅ Completed |
| Option 2 | Duplicate detection with UNIQUE constraint	| ✅ Completed |
| Option 1 | Professional CLI with argparse | ✅ Completed |
| Option 4 | Visualization with matplotlib & seaborn | ✅ Completed |

---

2. OPTION 3 – SCALING TO 10,000+ LOGS
What We Did

    Created scripts/generate_logs.py to generate 10,000+ synthetic log lines

    Ingested large logs into SQLite

    Measured performance with time and cProfile

Key Commands
bash

*Generate 10,000 logs*
python scripts/generate_logs.py 10000

*Ingest with timing*
time python -m src.ingest large_sample.log

*Profile performance*
python -m cProfile -s time -m src.ingest large_sample.log


Key Learnings
| Concept | What You Learned |
|---------|------------------|
| Profiling	| cProfile shows which functions take the most time |
| Bottleneck | _strptime (datetime parsing) was the slowest part |
| Generator efficiency | read_logs() streams logs without loading everything into memory |

---

3. OPTION 2 – DUPLICATE DETECTION
What We Did

    Added a UNIQUE constraint on (ip, timestamp_utc, method, url, status)

    Used INSERT OR IGNORE to skip duplicates silently

    Reported skipped entries to the user

Key Code Changes

```python
# In db.py - CREATE TABLE
CREATE TABLE IF NOT EXISTS logs (
    ...,
    UNIQUE(ip, timestamp_utc, method, url, status)  -- ← Prevents duplicates
)

# In db.py - INSERT
INSERT OR IGNORE INTO logs (...) VALUES (...)
```

**Key Learnings**
| Concept |	What You Learned |
|---------|------------------|
| UNIQUE constraint	| Prevents duplicate rows based on multiple columns |
| INSERT OR IGNORE | Skips duplicates instead of failing |
| Data quality | Ensuring analytics are accurate |

---

4. OPTION 1 – PROFESSIONAL CLI
What We Did

    Added argparse to ingest.py

    Created flags: --verbose, --limit, --query, --num-results

    Added help messages and examples

**Key Flags**
| Flag | What it does |
|------|--------------|
| --verbose	| Shows detailed progress |
| --limit 100 |	Processes only the first 100 lines |
| --query top-ips |	Runs a query after ingestion |
| --num-results 10 | Limits query results |

---

**Key Learnings**
| Concept |	What You Learned |
|---------|------------------|
| argparse | Build professional CLIs with help menus |
| Positional arguments | Required inputs (like filepath) |
| Optional arguments | Flags with -- (like --verbose) |

---

5. OPTION 4 – VISUALIZATION
What We Did

    Created src/visualize.py

    Generated three charts:

        Hourly Volume – traffic over time

        Status Distribution – success vs error rates

        Top IPs – highest traffic sources

**Key Libraries**
| Library |	Purpose |
|---------|---------|
| matplotlib | Core plotting library |
| seaborn |	Statistical visualizations |
| pandas | Data manipulation and SQL queries |

---

**Key Learnings**
| Concept |	What You Learned |
|---------|------------------|
| Plotting | How to create professional charts |
| DataFrames | How to work with tabular data |
| Saving outputs | plt.savefig() for PNG files |
| Ignoring outputs | *.png added to .gitignore |

---

6. NEW COMMANDS & CONCEPTS

| Command |	What it does |
|---------|--------------|
| ls -lh | List files with human-readable sizes |
| time python -m ... |	Measure execution time |
| chmod +x script.py |	Make a script executable |
| python -m cProfile -s time ... |	Profile code performance |
| > file.py	| Redirect output to a file (hangs if no input) |
| echo -n "" > file.py | Empty a file safely |
| 2>/dev/null |	Suppress error messages |

---

7. MASTER'S NOTE

    "We started with 5 lines of logs. Now we handle 10,000, detect duplicates, run a CLI, and generate charts. You've gone from script to system."

# PART 2: DETAILED CODE BREAKDOWNS

Each Python file—line-by-line dissection:

## 📘 CODE DEEP-DIVE: pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "smart-log-analyzer"
version = "0.1.0"
description = "Production-grade log parser with timezone handling"
readme = "README.md"
authors = [
    {name = "Bernard Omondi", email = "bernard@example.com"}
]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [
    "pytest>=7.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "pandas>=2.0.0",
]

**[project.optional-dependencies]**
dev = [
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "pytest-cov>=4.0.0",
]

[tool.black]
line-length = 88
target-version = ['py39', 'py310']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
```


### SECTION 1: [build-system] – HOW TO BUILD YOUR PACKAGE

```toml

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

| Field | Value	| Meaning |
|-------|-------|---------|
| requires | ["setuptools>=61.0", "wheel"] | Tools required to build your package |
| build-backend | "setuptools.build_meta" |	The backend that actually builds the package |

---

What this does:

    When someone runs pip install -e ., pip uses these tools to build your package

    setuptools is the standard Python build tool

    wheel is the format for distributing Python packages

**Analogy:** This is like saying "To build this house, you need a hammer (setuptools) and nails (wheel)."

### SECTION 2: [project] – WHAT YOUR PACKAGE IS

```toml
[project]
name = "smart-log-analyzer"
version = "0.1.0"
description = "Production-grade log parser with timezone handling"
readme = "README.md"
authors = [
    {name = "Bernard Omondi", email = "bernard@example.com"}
]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [...]
```

**Field Breakdown**
| Field | Value	| Meaning |
|-------|-------|---------|
| name | "smart-log-analyzer" |	The package name (what you import or pip install) |
| version |	"0.1.0"	| Semantic version (major.minor.patch) |
| description |	"Production-grade log parser..." |	Short description (appears on PyPI) |
| readme | "README.md" | The file shown on GitHub and PyPI |
| authors |	[{name, email}] | Who created this package |
| license | {text = "MIT"} | The license (MIT = permissive open source) |
| requires-python |	">=3.9"	Minimum Python version required |
| dependencies | [...] | Core dependencies – always installed |

---

**Dependencies Deep-Dive*
```toml
dependencies = [
    "pytest>=7.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "pandas>=2.0.0",
]

```

| Package |	Version	| Purpose |
|---------|---------|---------|
| pytest | >=7.0.0 | Testing framework |
| matplotlib | >=3.7.0 | Chart generation |
| seaborn |	>=0.12.0 |	Statistical visualizations (built on matplotlib) |
| pandas | >=2.0.0 | Data manipulation (used by visualize.py) |

---

**The** >= **means:** "Install version 7.0.0 or newer."

### SECTION 3: [project.optional-dependencies] – DEV DEPENDENCIES

```toml
**[project.optional-dependencies]**
dev = [
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "pytest-cov>=4.0.0",
]
```
| Package |	Purpose |
|---------|---------|
| black	| **Code formatter** – auto-formats your code to be consistent |
| ruff | **Linter** – finds code errors and style issues |
| mypy | **Type checker** – ensures you're using types correctly |
| pytest-cov | **Coverage tool** – shows which lines of code are tested |

Why optional-dependencies?

    These are not required to USE your package

    They are required to DEVELOP your package

    Installed with: pip install -e ".[dev]"

**Analogy:** If your package is a car, dependencies are the engine and wheels (needed to drive). dev dependencies are the tools in the garage (needed to build/fix the car).

### SECTION 4: [tool.black] – CODE FORMATTING CONFIG

```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310']
```

| Setting |	Value |	Meaning |
|---------|-------|---------|
| line-length |	88 | Maximum characters per line (Black's default is 88) |
| target-version | ['py39', 'py310'] | Black will format code to be compatible with Python 3.9 and 3.10 |

---

What this does:

    When you run black src/, it auto-formats your code

    It wraps lines that exceed 88 characters

    It ensures compatibility with Python 3.9+

Why 88? Black's opinionated default—they believe it's the perfect balance between readability and compactness.

### SECTION 5: [tool.ruff] – LINTING CONFIG

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

| Setting |	Value |	Meaning |
|---------|-------|---------|
| line-length |	88 | Match Black's line length |
| select |	["E", "F", "I", "N", "W"] |	Which rules to enable |
| ignore |	["E501"] |	Which rules to disable |

---

**Rule categories:**
| Code | Category |	Example |
|------|----------|---------|
| E | Errors | Syntax errors, undefined variables |
| F | Pyflakes | Unused imports, undefined names |
| I	| Import sorting | Organizing imports alphabetically |
| N	| Naming | function_name vs functionName |
| W	| Warnings | Code that's valid but questionable |

---

**Why ignore** E501? E501 is "line too long" – but Black already handles line length, so ruff doesn't need to warn about it.

### SECTION 6: [tool.mypy] – TYPE CHECKING CONFIG

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
```

| Setting |	Value |	Meaning |
|---------|-------|---------|
| python_version | "3.9" |	Which Python version to check against |
| warn_return_any |	true |	Warn if a function returns Any type |
| warn_unused_configs |	true |	Warn if a config setting is unused |

---

What this does:

    mypy checks your type hints (def parse_line(line: str) -> dict:)

    It ensures you're using types correctly

    warn_return_any catches functions that aren't properly typed

**Example:**

```python

# This would trigger a warning:
def get_data():  # No return type
    return "hello"

# This is correct:
def get_data() -> str:  # ✅ Type declared
    return "hello"
```

#### COMPLETE ANATOMY DIAGRAM

text

┌─────────────────────────────────────────────────────────────────┐
│                     pyproject.toml                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [build-system]                                         │  │
│  │  │                                                     │  │
│  │  └── How to build the package                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [project]                                              │  │
│  │  │                                                     │  │
│  │  ├── name, version, description  ──── Identity        │  │
│  │  ├── authors, license, readme     ──── Metadata       │  │
│  │  ├── requires-python              ──── Compatibility   │  │
│  │  └── dependencies                 ──── Core deps       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [project.optional-dependencies]                        │  │
│  │  │                                                     │  │
│  │  └── dev = [...]  ──── Development tools              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [tool.black]    ──── Formatting                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  [tool.ruff]     ──── Linting                          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  [tool.mypy]     ──── Type checking                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

**QUICK REFERENCE**

| Section |	Purpose | When to edit |
|---------|---------|--------------|
| [build-system] | Build tools | Almost never |
| [project] → name | Package name |	Never (it's set) |
| [project] → version |	Package version | When you release new version |
| [project] → dependencies | Core deps	When you add a new library |
| [project.optional-dependencies] |	Dev deps |	When you add a new dev tool |
| [tool.black] | Formatting | If you want to change style |
| [tool.ruff] |	Linting | If you want to change rules |
| [tool.mypy] |	Type checking |	If you want to change strictness |

---

## 📘 CODE DEEP-DIVE: parser.py
```python
import re
from datetime import datetime, timezone, timedelta
import sys
```
| Line | What it does |	Why |
|------|--------------|-----|
| import re | Imports the regular expression module | For parsing log lines with patterns |
| from datetime import ... | Imports datetime components | For parsing and converting timestamps |
| import sys | Imports system functions	| For error output (stderr) |

---

```python

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<url>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)
```
| Part | What it captures | Example |
|------|------------------|---------|
| (?P<ip>\S+) |	IP address (non-space chars) | 127.0.0.1 |
| \S+ \S+ |	Two fields (ident, authuser) |	- frank |
| \[(?P<timestamp>[^\]]+)\]	| Timestamp inside brackets | 10/Oct/2000:13:55:36 -0700
| (?P<method>\S+) |	HTTP method	| GET |
| (?P<url>\S+) | URL path |	/apache_pb.gif |
| \S+ |	HTTP version | HTTP/1.0 |
| (?P<status>\d{3}) | Status code (3 digits) | 200 |
| (?P<size>\S+) | Size (bytes or -) | 2326 or - |
| re.compile() | pre-compiles the regex for speed—we call it once, not every time we parse a line. | |

---

```python

def parse_line(line: str):
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    data = match.groupdict()
```
| Line | What it does |
|------|--------------|
| def parse_line(line: str): |	Function that takes a string, returns a dict |
| match = LOG_PATTERN.match(line) |	Applies regex to the line |
| if not match:	| If regex doesn't match, it's a malformed line |
| return None |	Skip malformed lines |
| data = match.groupdict() | Converts regex groups into a dictionary |

---

```python

    time_str = data['timestamp']
    parts = time_str.rsplit(' ', 1)
    dt_part = parts[0]  # "10/Oct/2000:13:55:36"
    tz_part = parts[1] if len(parts) > 1 else "+0000"
```
| Line | What it does |
|------|--------------|
| time_str = data['timestamp'] | Gets timestamp: "10/Oct/2000:13:55:36 -0700" |
| parts = time_str.rsplit(' ', 1) |	Splits from the right ONCE: ["10/Oct/2000:13:55:36", "-0700"] |
| dt_part = parts[0] |	The datetime part |
| tz_part = parts[1] if len(parts) > 1 else "+0000" | Timezone offset, or default to UTC |

---

```python

    dt_naive = datetime.strptime(dt_part, '%d/%b/%Y:%H:%M:%S')
```

| Directive | Meaning |	Example |
|-----------|---------|---------|
| %d |	Day of month | 10 |
| %b |	Month abbreviation | Oct |
| %Y |	Year | 2000 |
| %H |	Hour (24-hour) | 13 |
| %M |	Minute | 55 |
| %S |	Second | 36 |

---

```python

    sign = tz_part[0]  # '+' or '-'
    hours = int(tz_part[1:3])
    minutes = int(tz_part[3:5])
    offset_seconds = (hours * 3600 + minutes * 60)
    if sign == '-':
        offset_seconds = -offset_seconds
```
| Line | What it does | Example |
|------|--------------|---------|
| sign = tz_part[0]	| Gets the plus or minus | - |
| hours = int(tz_part[1:3]) | Extracts hours | 07 |
| minutes = int(tz_part[3:5]) |	Extracts minutes | 00 |
| offset_seconds = (hours * 3600 + minutes * 60) | Converts to seconds | 25200 |
| if sign == '-': offset_seconds = -offset_seconds | Makes negative for West | -25200 |

---

```python

    tz = timezone(timedelta(seconds=offset_seconds))
    dt_local = dt_naive.replace(tzinfo=tz)
    dt_utc = dt_local.astimezone(timezone.utc)
```
| Line | What it does |
|------|--------------|
| tz = timezone(timedelta(seconds=offset_seconds)) | Creates a timezone object from offset |
| dt_local = dt_naive.replace(tzinfo=tz) | Attaches the timezone to the datetime |
| dt_utc = dt_local.astimezone(timezone.utc) | Converts to UTC |

---

```python

    data['timestamp_local'] = dt_local
    data['timestamp_utc'] = dt_utc
    data['timezone_offset'] = tz_part
    data['timestamp'] = dt_utc
```
| Line | What it does |
|------|--------------|
| data['timestamp_local'] = dt_local | Original timestamp with offset |
| data['timestamp_utc'] = dt_utc | Converted to UTC |
| data['timezone_offset'] = tz_part	| Original offset string |
| data['timestamp'] = dt_utc | For backward compatibility |

---

```python

    data['status'] = int(data['status'])
    size = data['size']
    data['size'] = int(size) if size != '-' else None
    return data
```
| Line | What it does |
|------|--------------|
| data['status'] = int(data['status']) | Converts status to integer |
| size = data['size'] |	Gets size as string |
| int(size) if size != '-' else None |	Converts to int, or None for missing |
| return data |	Returns the parsed dictionary |

---

```python

def read_logs(filepath: str):
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parsed = parse_line(line)
            if parsed:
                yield parsed
            else:
                print(f"Failed to parse: {line[:50]}...", file=sys.stderr)
```
| Line | What it does |
|------|--------------|
| with open(filepath, 'r') as f: | Opens file safely (auto-closes) |
| for line in f: |	Iterates line by line (streaming) |
| line = line.strip() |	Removes newline and whitespace |
| if not line: | Skips empty lines |
| parsed = parse_line(line) | Parses the line |
| yield parsed | Generator – returns one at a time |
| print(..., file=sys.stderr) |	Prints errors to stderr (not stdout) |

---

Why yield? It streams logs instead of loading all into memory.

## 📘 CODE DEEP-DIVE: db.py

```python

import sqlite3
from datetime import datetime
from typing import List, Dict

DB_PATH = "logs.db"
```
| Line | What it does |
|------|--------------|
| import sqlite3 | SQLite database driver (built into Python) |
| from datetime import datetime | For timestamps |
| from typing import List, Dict | Type hints (optional but helpful) |
| DB_PATH = "logs.db" |	The database file name |

---

```python

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```
| Line | What it does |
|------|--------------|
| sqlite3.connect(DB_PATH) | Creates/opens database |
| conn.row_factory = sqlite3.Row | Allows column access by name (row['ip']) |
| return conn |	Returns the connection object |

---

```python

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            timestamp_utc DATETIME NOT NULL,
            timestamp_local DATETIME NOT NULL,
            timezone_offset TEXT NOT NULL,
            method TEXT NOT NULL,
            url TEXT NOT NULL,
            status INTEGER NOT NULL,
            size INTEGER,
            UNIQUE(ip, timestamp_utc, method, url, status)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ip ON logs(ip)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp_utc)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON logs(status)")
    
    conn.commit()
    conn.close()
```

| Component | What it does |
|-----------|--------------|
| CREATE TABLE IF NOT EXISTS | Creates table only if it doesn't exist |
| id INTEGER PRIMARY KEY AUTOINCREMENT | Auto-incrementing unique ID |
| TEXT NOT NULL	| Text column that can't be empty |
| DATETIME | SQLite stores as text, but Python handles it |
| UNIQUE(...) |	Prevents duplicates (your deduplication!) |
| CREATE INDEX | Speeds up queries on those columns |
| conn.commit() | Saves changes |
| conn.close() | Closes the connection |

--- 

```python

def insert_logs(logs: List[Dict]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    
    for log in logs:
        cursor.execute("""
            INSERT OR IGNORE INTO logs (
                ip, timestamp_utc, timestamp_local, timezone_offset,
                method, url, status, size
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log['ip'],
            log['timestamp_utc'].isoformat(),
            log['timestamp_local'].isoformat(),
            log['timezone_offset'],
            log['method'],
            log['url'],
            log['status'],
            log['size']
        ))
        
        if cursor.rowcount == 1:
            inserted += 1
        else:
            skipped += 1
    
    conn.commit()
    conn.close()
    
    if skipped > 0:
        print(f"⚠️ Skipped {skipped} duplicate log entries")
    
    return inserted
```

| Part | What it does |
|------|--------------|
| INSERT OR IGNORE | Skips duplicates instead of failing |
| (?, ?, ?, ..., ?)	| Placeholders – prevents SQL injection |
| .isoformat() | Converts datetime to string 2026-08-14T08:00:00 |
| cursor.rowcount |	Number of rows affected (1 = inserted, 0 = duplicate) |
| skipped > 0 |	Reports duplicates to the user | 

--- 

```python

def query_top_ips(limit: int = 5) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ip, COUNT(*) as request_count
        FROM logs
        GROUP BY ip
        ORDER BY request_count DESC
        LIMIT ?
    """, (limit,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results
```
| Part | What it does |
|------|--------------|
| GROUP BY ip |	Groups logs by IP address |
| COUNT(*) | Counts rows in each group |
| ORDER BY request_count DESC |	Highest count first |
| LIMIT ? |	Only returns top N (prevents overload) |
| (limit,) | Tuple with one value (needed for SQLite)
| [dict(row) for row in ...] |	Converts rows to dictionaries |

---

## 📘 CODE DEEP-DIVE: ingest.py
```python

import sys
import argparse
from src.parser import read_logs
from src.db import insert_logs, get_connection, create_table, query_top_ips, query_hourly_volume, query_error_rate
```
| Line | What it does |
|------|--------------|
| import sys |	For command-line arguments and system functions |
| import argparse |	For building the CLI |
| from src.parser import read_logs | Imports the parsing function |
| from src.db import ... |	Imports database functions |

---

```python

def ingest_logs(filepath: str, verbose: bool = False, limit: int = None):
    create_table()
    
    if verbose:
        print(f"📖 Reading logs from {filepath}...")
    
    logs = list(read_logs(filepath))
    
    if limit:
        logs = logs[:limit]
        if verbose:
            print(f"✅ Limiting to {limit} log entries")
    
    if verbose:
        print(f"✅ Parsed {len(logs)} log entries")
    
    rows = insert_logs(logs)
    
    if verbose:
        print(f"✅ Inserted {rows} logs into database")
```

| Line | What it does |
|------|--------------|
| def ingest_logs(filepath, verbose=False, limit=None):	| Main orchestration function
| create_table() |	Ensures database exists |
| if verbose: |	Conditionally shows progress |
| logs = list(read_logs(filepath)) | Parses ALL logs into a list |
| if limit:	| Truncates to first N logs |
| rows = insert_logs(logs) | Inserts into database |

---

Note: list(read_logs(filepath)) loads everything into memory. For 10,000 logs, this is fine. For 10 million, you'd need a different approach.
python

def main():
    parser = argparse.ArgumentParser(
        description="Ingest log files into the smart-log-analyzer database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.ingest sample.log
  python -m src.ingest large_sample.log --verbose
  python -m src.ingest large_sample.log --limit 100 --verbose
  python -m src.ingest large_sample.log --query top-ips --limit 10
        """
    )

| Part | What it does |
|------|--------------|
| argparse.ArgumentParser(...) | Creates the CLI parser |
| description= | Shown when user runs --help |
| epilog= | Shown AFTER the help menu |
| RawDescriptionHelpFormatter |	Preserves formatting in epilog |

---

```python

    parser.add_argument(
        'filepath',
        help='Path to the log file to ingest'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress'
    )
    parser.add_argument(
        '-l', '--limit',
        type=int,
        help='Maximum number of logs to ingest (e.g., --limit 100)'
    )
    parser.add_argument(
        '-q', '--query',
        choices=['top-ips', 'hourly-volume', 'error-rate'],
        help='Run a query after ingestion'
    )
    parser.add_argument(
        '-n', '--num-results',
        type=int,
        default=5,
        help='Number of results for query (default: 5)'
    )
```
| Argument | Type |	What it does |
|----------|------|--------------|
| filepath | Positional | The log file to process |
| -v/--verbose | Flag (store_true) | Enables verbose output |
| -l/--limit | Integer | Limits the number of logs processed |
| -q/--query | Choice | Runs a query after ingestion |
| -n/--num-results | Integer |	Limits query results |

---

```python

    args = parser.parse_args()
    
    # Ingest logs
    ingest_logs(args.filepath, verbose=args.verbose, limit=args.limit)
    
    # Run query if requested
    if args.query:
        print(f"\n=== {args.query.replace('-', ' ').title()} ===")
        
        if args.query == 'top-ips':
            results = query_top_ips(args.num_results)
            for row in results:
                print(f"  {row['ip']}: {row['request_count']} requests")
        
        elif args.query == 'hourly-volume':
            results = query_hourly_volume()
            for row in results:
                print(f"  {row['hour']}: {row['request_count']} requests")
        
        elif args.query == 'error-rate':
            results = query_error_rate()
            for row in results[:args.num_results]:
                print(f"  {row['url']}: {row['error_rate']}% errors ({row['error_count']}/{row['total_requests']})")
```
| Line | What it does |
|------|--------------|
| args = parser.parse_args() |	Parses command-line arguments |
| ingest_logs(...) | Orchestrates the pipeline |
| if args.query: |	Runs a query if requested |
| query_top_ips(args.num_results) |	Delegates to db.py |

---

## 📘 CODE DEEP-DIVE: visualize.py
```python

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.db import get_connection
```

| Library |	Purpose |
|---------|---------|
| matplotlib.pyplot	| Core plotting library |
| seaborn |	Statistical visualizations (built on matplotlib) |
| pandas | Data manipulation and SQL queries |
| src.db | Database connection |

---

```python

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
```

| Line | What it does |
|------|--------------|
| sns.set_style("whitegrid") |	Sets a professional chart style |
| plt.rcParams['figure.figsize'] = (12, 6) | Default chart size (width, height in inches) |
| plt.rcParams['font.size'] = 10 | Default font size |

---

```python

def fetch_hourly_data():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT 
            timestamp_utc,
            strftime('%Y-%m-%d %H:00:00', timestamp_utc) as hour,
            COUNT(*) as request_count
        FROM logs
        GROUP BY hour
        ORDER BY hour ASC
    """, conn)
    conn.close()
    df['hour'] = pd.to_datetime(df['hour'])
    return df
```

| Part | What it does |
|------|--------------|
| pd.read_sql_query() | Runs SQL query and returns a DataFrame |
| strftime('%Y-%m-%d %H:00:00', timestamp_utc) | Groups by hour (truncates minutes/seconds) |
| COUNT(*) as request_count	| Counts requests per hour |
| ORDER BY hour ASC	| Sorts chronologically |
| df['hour'] = pd.to_datetime(df['hour']) |	Converts string to datetime for plotting |

--

```python

def plot_hourly_volume(save_path='hourly_volume.png'):
    df = fetch_hourly_data()
    
    plt.figure(figsize=(14, 6))
    plt.plot(df['hour'], df['request_count'], marker='o', linestyle='-', linewidth=2, markersize=4)
    plt.title('Hourly Request Volume', fontsize=16, fontweight='bold')
    plt.xlabel('Hour', fontsize=12)
    plt.ylabel('Number of Requests', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved hourly volume chart to {save_path}")
    plt.show()
```

| Line | What it does |
|------|--------------|
| plt.figure(figsize=(14, 6)) |	Creates a new figure with custom size |
| plt.plot(df['hour'], df['request_count'], ...) |	Line plot with markers |
| marker='o' |	Circular markers at each data point |
| linestyle='-'	| Solid line |
| linewidth=2 |	Thicker line |
| plt.title(..., fontweight='bold') | Bold title |
| plt.xticks(rotation=45, ha='right') |	Rotates X-axis labels for readability |
| plt.tight_layout() | Prevents clipping of labels |
| plt.savefig(save_path, dpi=150, ...)	| Saves as high-resolution PNG |
| plt.show() |	Displays the chart |

---

```python

def plot_status_distribution(save_path='status_distribution.png'):
    df = fetch_status_data()
    
    colors = []
    for status in df['status']:
        if status < 300:
            colors.append('green')
        elif status < 400:
            colors.append('blue')
        elif status < 500:
            colors.append('orange')
        else:
            colors.append('red')
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df['status'].astype(str), df['count'], color=colors)
```

| Part | What it does |
|------|--------------|
| colors = [] |	Creates a list for color-coding bars |
| if status < 300: | Success codes → green |
| elif status < 400: |	Redirection → blue |
| elif status < 500: |	Client errors → orange |
| else:	| Server errors → red |
| plt.bar(df['status'].astype(str), ...) |	Bar chart with string labels |

---


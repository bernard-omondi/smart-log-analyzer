# Smart Log Analyzer - Design Document

## 1. Architecture Overview
[Streaming vs chunking? why? Memory estimate?]

## 3. Database Schema
```sql
CREATE TABLE logs (
	id INTEGER PRIMARY KEY,
	ip TEXT,
	timestamp DATETIME,
	method TEXT,
	url TEXT,
	status INTEGER,
	size INTEGER,
	user_agent TEXT
);

### 4. Write your parsing function

Create `log_parser.py`:

```python
import re
from datetime import datetime
from typing import Optional, Dict

# Apache combined log format
# Example: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<url>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)

def parse_log_line(line: str) -> Optional[Dict]:
    """
    Parse a single Apache combined log line.
    
    Args:
        line: Raw log line string
    
    Returns:
        Dict with keys: ip, timestamp, method, url, status, size
        None if parsing fails
    
    Example:
        >>> parse_log_line('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326')
        {'ip': '127.0.0.1', 'timestamp': '2000-10-10 13:55:36-07:00', ...}
    """
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    
    data = match.groupdict()
    
    # TODO: Convert timestamp to ISO format with timezone
    # TODO: Handle '-' size (missing) -> convert to None or 0
    
    return data
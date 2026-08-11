import re
from datetime import datetime, timezone, timedelta
import sys

# Apache combined log format
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<url>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)

def parse_line(line):
    """Parse one log line into a dict with timezone handling."""
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    
    data = match.groupdict()
    
    # Parse timestamp WITH timezone
    time_str = data['timestamp']  # "10/Oct/2000:13:55:36 -0700"
    
    # Split timestamp and timezone
    parts = time_str.rsplit(' ', 1)
    dt_part = parts[0]  # "10/Oct/2000:13:55:36"
    tz_part = parts[1] if len(parts) > 1 else "+0000"  # "-0700" or default UTC
    
    # Parse datetime without timezone
    dt_naive = datetime.strptime(dt_part, '%d/%b/%Y:%H:%M:%S')
    
    # Parse timezone offset (e.g., "-0700" → -7 hours)
    sign = tz_part[0]  # '+' or '-'
    hours = int(tz_part[1:3])
    minutes = int(tz_part[3:5])
    offset_seconds = (hours * 3600 + minutes * 60)
    if sign == '-':
        offset_seconds = -offset_seconds
    
    # Create timezone-aware datetime
    tz = timezone(timedelta(seconds=offset_seconds))
    dt_local = dt_naive.replace(tzinfo=tz)
    
    # Convert to UTC
    dt_utc = dt_local.astimezone(timezone.utc)
    
    # Store both versions
    data['timestamp_local'] = dt_local
    data['timestamp_utc'] = dt_utc
    data['timezone_offset'] = tz_part
    
    # Also keep a simple timestamp for backward compatibility
    data['timestamp'] = dt_utc
    
    # Convert status to int
    data['status'] = int(data['status'])
    
    # Convert size to int, handle '-' as None
    size = data['size']
    data['size'] = int(size) if size != '-' else None
    
    return data

def read_logs(filepath):
    """Generator that yields parsed lines one by one."""
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

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for entry in read_logs(sys.argv[1]):
            print(f"IP: {entry['ip']}")
            print(f"  Local: {entry['timestamp_local']}")
            print(f"  UTC:   {entry['timestamp_utc']}")
            print(f"  Offset: {entry['timezone_offset']}")
            print(f"  {entry['method']} {entry['url']} → {entry['status']} ({entry['size']} bytes)")
            print()
    else:
        print("Usage: python -m src.parser sample.log")

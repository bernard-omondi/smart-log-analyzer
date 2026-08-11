import re
from datetime import datetime
import sys

# Apache combined log format
# Example: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<url>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)

def parse_line(line):
    """Parse one log line into a dict."""
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    
    data = match.groupdict()
    
    # Convert timestamp string to datetime object
    # Example: "10/Oct/2000:13:55:36 -0700"
    time_str = data['timestamp']
    # Remove timezone for now (we'll handle later)
    time_part = time_str.rsplit(' ', 1)[0]  # "10/Oct/2000:13:55:36"
    dt = datetime.strptime(time_part, '%d/%b/%Y:%H:%M:%S')
    data['timestamp'] = dt
    
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
                # Print error to stderr (won't affect output)
                print(f"Failed to parse: {line[:50]}...", file=sys.stderr)

# If run directly, test it
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for entry in read_logs(sys.argv[1]):
            print(entry)
    else:
        print("Usage: python -m src.parser sample.log")

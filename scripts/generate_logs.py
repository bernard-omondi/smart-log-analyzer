#!/usr/bin/env python3
"""
Generate synthetic log files for testing.
Usage: python scripts/generate_logs.py [number_of_lines]
"""

import random
import datetime
import sys
import os

# Sample data for realistic log generation
IPS = [
    '192.168.1.1', '192.168.1.2', '192.168.1.3',
    '10.0.0.1', '10.0.0.2', '10.0.0.3',
    '172.16.0.1', '172.16.0.2',
    '203.0.113.5', '198.51.100.7', '8.8.8.8'
]

METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

URLS = [
    '/api/login', '/api/logout', '/api/users',
    '/dashboard', '/reports', '/settings',
    '/index.html', '/about', '/contact',
    '/products', '/cart', '/checkout',
    '/user/123', '/user/456', '/user/789',
    '/download/file1.pdf', '/download/file2.zip'
]

STATUS_CODES = [200, 200, 200, 200, 301, 302, 400, 401, 403, 404, 500, 502]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'curl/7.68.0',
    'Python-urllib/3.8',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
]

def random_date():
    """Generate a random date within the last 365 days."""
    days_ago = random.randint(0, 365)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    seconds_ago = random.randint(0, 59)
    
    dt = datetime.datetime.now() - datetime.timedelta(
        days=days_ago,
        hours=hours_ago,
        minutes=minutes_ago,
        seconds=seconds_ago
    )
    return dt

def generate_log_line():
    """Generate a single Apache-style log line."""
    ip = random.choice(IPS)
    user = '-' if random.random() > 0.3 else random.choice(['admin', 'jane', 'frank', 'john'])
    
    dt = random_date()
    timestamp_str = dt.strftime('%d/%b/%Y:%H:%M:%S +0000')
    
    method = random.choice(METHODS)
    url = random.choice(URLS)
    status = random.choice(STATUS_CODES)
    size = random.randint(50, 10000) if status != 404 else '-'
    user_agent = random.choice(USER_AGENTS)
    
    return f'{ip} - {user} [{timestamp_str}] "{method} {url} HTTP/1.1" {status} {size} "{user_agent}"'

def generate_log_file(num_lines, filepath='large_sample.log'):
    """Generate a log file with the specified number of lines."""
    print(f"📝 Generating {num_lines:,} log lines...")
    
    with open(filepath, 'w') as f:
        for i in range(num_lines):
            f.write(generate_log_line() + '\n')
            # Show progress every 1000 lines
            if (i + 1) % 1000 == 0:
                print(f"  ... {i+1:,} lines written")
    
    file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
    print(f"✅ Generated {num_lines:,} lines in {filepath}")
    print(f"📦 File size: {file_size:.2f} MB")

if __name__ == '__main__':
    # Parse command-line argument
    num_lines = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    generate_log_file(num_lines)

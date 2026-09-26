import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


# --- Database selection ---
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None and DATABASE_URL.startswith("postgres")

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
DB_PATH = "logs.db"

def get_connection():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn     

def create_table():
    """Create the logs table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                ip TEXT NOT NULL,
                timestamp_utc TIMESTAMP NOT NULL,
                timestamp_local TIMESTAMP NOT NULL,
                timezone_offset TEXT NOT NULL,
                method TEXT NOT NULL,
                url TEXT NOT NULL,
                status INTEGER NOT NULL,
                size INTEGER,
                UNIQUE(ip, timestamp_utc, method, url, status)
            )
        """)
    else:
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

    engine = "PostgreSQL" if USE_POSTGRES else "SQLite"
    print(f"✅ Database and indexes created successfully ({engine}).")


def insert_logs(logs: List[Dict]) -> int:
    """Insert multiple log entries, skipping duplicates."""
    if not logs:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        insert_sql = """
            INSERT INTO logs (
                ip, timestamp_utc, timestamp_local, timezone_offset,
                method, url, status, size
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
    else:
        insert_sql = """
            INSERT OR IGNORE INTO logs (
                ip, timestamp_utc, timestamp_local, timezone_offset,
                method, url, status, size
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

    inserted = 0
    skipped = 0

    for log in logs:
        try:
            cursor.execute(insert_sql, (
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
        except Exception as e:
            print(f"⚠️ Error inserting log: {e}")
            continue

    conn.commit()
    conn.close()

    if skipped > 0:
        print(f"⚠️ Skipped {skipped} duplicate log entries")

    return inserted


def query_top_ips(limit: int = 5) -> List[Dict]:
    """Get top IPs by request count."""
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

def query_hourly_volume() -> List[Dict]:
    """Get hourly request volume."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("""
            SELECT
                TO_CHAR(timestamp_utc, 'YYYY-MM-DD HH24:00:00') as hour,
                COUNT(*) as request_count
            FROM logs
            GROUP BY hour
            ORDER BY hour ASC
        """)
    else:
        cursor.execute("""
            SELECT
                strftime('%Y-%m-%d %H:00:00', timestamp_utc) as hour,
                COUNT(*) as request_count
            FROM logs
            GROUP BY hour
            ORDER BY hour ASC
        """)

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def query_error_rate() -> List[Dict]:
    """Get error rate (5xx) per endpoint."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            url,
            COUNT(*) as total_requests,
            SUM(CASE WHEN status >= 500 THEN 1 ELSE 0 END) as error_count,
            ROUND(100.0 * SUM(CASE WHEN status >= 500 THEN 1 ELSE 0 END) / COUNT(*), 2) as error_rate
        FROM logs
        GROUP BY url
        HAVING error_count > 0
        ORDER BY error_rate DESC
    """)
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def test_database():
    """Test the database functions with sample data."""
    create_table()
    
    # Sample data (matching our logs)
    sample_logs = [
        {
            'ip': '127.0.0.1',
            'timestamp_utc': datetime(2000, 10, 10, 20, 55, 36),
            'timestamp_local': datetime(2000, 10, 10, 13, 55, 36),
            'timezone_offset': '-0700',
            'method': 'GET',
            'url': '/apache_pb.gif',
            'status': 200,
            'size': 2326
        },
        {
            'ip': '192.168.1.1',
            'timestamp_utc': datetime(2021, 11, 20, 9, 12, 44),
            'timestamp_local': datetime(2021, 11, 20, 9, 12, 44),
            'timezone_offset': '+0000',
            'method': 'POST',
            'url': '/api/login',
            'status': 401,
            'size': 512
        },
        {
            'ip': '10.0.2',
            'timestamp_utc': datetime(2021, 12, 31, 18, 30, 1),
            'timestamp_local': datetime(2022, 1, 1, 0, 0, 1),
            'timezone_offset': '+0530',
            'method': 'GET',
            'url': '/dashboard',
            'status': 200,
            'size': 4096
        },
        {
            'ip': '203.0.113.5',
            'timestamp_utc': datetime(2023, 3, 16, 2, 15, 30),
            'timestamp_local': datetime(2023, 3, 15, 22, 15, 30),
            'timezone_offset': '-0400',
            'method': 'DELETE',
            'url': '/user/123',
            'status': 403,
            'size': 128
        },
        {
            'ip': '198.51.100.7',
            'timestamp_utc': datetime(2024, 6, 30, 16, 30, 22),
            'timestamp_local': datetime(2024, 6, 30, 18, 30, 22),
            'timezone_offset': '+0200',
            'method': 'GET',
            'url': '/report.pdf',
            'status': 404,
            'size': None
        }
    ]
    
    # Insert sample logs
    rows = insert_logs(sample_logs)
    print(f"✅ Inserted {rows} logs into database")
    
    # Run queries
    print("\n=== Top IPs ===")
    for row in query_top_ips():
        print(f"  {row['ip']}: {row['request_count']} requests")
    
    print("\n=== Hourly Volume ===")
    for row in query_hourly_volume():
        print(f"  {row['hour']}: {row['request_count']} requests")
    
    print("\n=== Error Rate per Endpoint ===")
    for row in query_error_rate():
        print(f"  {row['url']}: {row['error_rate']}% errors ({row['error_count']}/{row['total_requests']})")

if __name__ == '__main__':
    test_database()

import sys
import argparse
from src.parser import read_logs
from src.db import insert_logs, get_connection, create_table, query_top_ips, query_hourly_volume, query_error_rate

def ingest_logs(filepath: str, verbose: bool = False, limit: int = None):
    """
    Ingest a log file into the database.
    
    Args:
        filepath: Path to the log file
        verbose: Print detailed progress
        limit: Maximum number of logs to ingest (None = all)
    """
    
    # Ensure database exists
    create_table()
    
    # Parse logs
    if verbose:
        print(f"📖 Reading logs from {filepath}...")
    
    logs = list(read_logs(filepath))
    
    if limit:
        logs = logs[:limit]
        if verbose:
            print(f"✅ Limiting to {limit} log entries")
    
    if verbose:
        print(f"✅ Parsed {len(logs)} log entries")
    
    # Insert into database
    rows = insert_logs(logs)
    
    if verbose:
        print(f"✅ Inserted {rows} logs into database")
    
    # Show summary
    conn = get_connection()
    cursor = conn.cursor()
    
    # Count total rows
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]
    
    # Show date range
    cursor.execute("""
        SELECT 
            MIN(timestamp_utc) as first,
            MAX(timestamp_utc) as last
        FROM logs
    """)
    row = cursor.fetchone()
    first = row[0]
    last = row[1]
    
    conn.close()
    
    if verbose:
        print(f"\n📊 Database Summary:")
        print(f"   Total logs: {total}")
        print(f"   Date range: {first} to {last}")

def main():
    """Command-line entry point."""
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
    
    args = parser.parse_args()
    
    # If query-only mode (no ingestion)
    if args.query and not args.filepath:
        print("Please provide a filepath for ingestion")
        sys.exit(1)
    
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

if __name__ == '__main__':
    main()

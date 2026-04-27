#!/usr/bin/env python3
"""
Performance benchmark script to measure query execution time before/after indexes.
Simulates common query patterns and measures performance improvements.
"""

import sqlite3
import time
from pathlib import Path
from typing import Dict, List
import random
import string


def get_db_path() -> Path:
    """Get the database path."""
    return Path(__file__).parent / "forgeos.db"


def generate_test_data(conn: sqlite3.Connection, num_records: int = 1000):
    """Generate test data for benchmarking."""
    cursor = conn.cursor()
    
    # Check if we already have enough test data
    count = cursor.execute("SELECT COUNT(*) FROM organization").fetchone()[0]
    if count >= 1:
        print(f"✓ Test data already exists ({count} organizations)")
        return
    
    print(f"Generating {num_records} test records...")
    
    # Create test organization
    cursor.execute(
        "INSERT OR IGNORE INTO organization (id, name, slug, plan, created_at, updated_at) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
        ("bench-org", "Benchmark Org", "benchmark", "pro")
    )
    
    conn.commit()
    cursor.close()
    print("✓ Test data generated")


def benchmark_query(conn: sqlite3.Connection, query: str, params: tuple, iterations: int = 100) -> float:
    """Benchmark a query by running it multiple times and returning average time in ms."""
    cursor = conn.cursor()
    
    # Warm up
    cursor.execute(query, params)
    cursor.fetchall()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        cursor.execute(query, params)
        cursor.fetchall()
    end = time.perf_counter()
    
    cursor.close()
    avg_time_ms = ((end - start) / iterations) * 1000
    return avg_time_ms


def run_benchmarks(conn: sqlite3.Connection) -> Dict[str, float]:
    """Run all benchmark queries and return results."""
    print("\nRunning performance benchmarks...")
    print("(Each query executed 100 times, average reported)\n")
    
    benchmarks = {
        "PipelineRun - Active runs": (
            "SELECT * FROM pipelinerun WHERE organization_id = ? AND deleted = 0 ORDER BY created_at DESC LIMIT 20",
            ("bench-org",)
        ),
        "CalendarEvent - Non-cancelled": (
            "SELECT * FROM calendarevent WHERE organization_id = ? AND status != 'cancelled' ORDER BY start_at LIMIT 20",
            ("bench-org",)
        ),
        "CalendarEvent - Offline sync": (
            "SELECT * FROM calendarevent WHERE organization_id = ? AND sync_status = 'offline' LIMIT 20",
            ("bench-org",)
        ),
        "Deliverable - Active by status": (
            "SELECT * FROM deliverable WHERE organization_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 20",
            ("bench-org",)
        ),
        "Brief - User briefs": (
            "SELECT * FROM brief WHERE organization_id = ? AND user_id = ? ORDER BY created_at DESC LIMIT 20",
            ("bench-org", "user-123")
        ),
        "Project - Active projects": (
            "SELECT * FROM project WHERE organization_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 20",
            ("bench-org",)
        ),
        "ScrapeItem - Top scored": (
            "SELECT * FROM scrapeitem WHERE organization_id = ? AND dismissed_at IS NULL ORDER BY score DESC, created_at DESC LIMIT 20",
            ("bench-org",)
        ),
        "UsageEvent - User usage": (
            "SELECT * FROM usageevent WHERE organization_id = ? AND user_id = ? ORDER BY occurred_at DESC LIMIT 100",
            ("bench-org", "user-123")
        ),
        "AuditEvent - User audit log": (
            "SELECT * FROM auditevent WHERE organization_id = ? AND user_id = ? ORDER BY created_at DESC LIMIT 50",
            ("bench-org", "user-123")
        ),
        "ChatMessage - Session messages": (
            "SELECT * FROM chatmessage WHERE organization_id = ? AND session_id = 1 ORDER BY created_at LIMIT 100",
            ("bench-org",)
        ),
    }
    
    results = {}
    for name, (query, params) in benchmarks.items():
        try:
            avg_ms = benchmark_query(conn, query, params, iterations=100)
            results[name] = avg_ms
            
            # Color code based on performance
            if avg_ms < 1.0:
                color = "🟢"
            elif avg_ms < 5.0:
                color = "🟡"
            else:
                color = "🔴"
            
            print(f"{color} {name:35} {avg_ms:>8.3f} ms")
        except Exception as e:
            print(f"❌ {name:35} ERROR: {str(e)}")
            results[name] = -1
    
    return results


def show_index_stats(conn: sqlite3.Connection):
    """Show statistics about database indexes."""
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("INDEX STATISTICS")
    print("=" * 80)
    
    # Count indexes
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
    idx_count = cursor.fetchone()[0]
    
    # Get database size
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    db_size_mb = (page_count * page_size) / (1024 * 1024)
    
    print(f"\nTotal custom indexes: {idx_count}")
    print(f"Database size: {db_size_mb:.2f} MB")
    
    # Show indexes per table - extract table name from index name pattern idx_tablename_*
    cursor.execute("""
        SELECT 
            CASE 
                WHEN name LIKE 'idx_%_%' THEN substr(name, 5, length(name) - 4)
                ELSE 'unknown'
            END as table_prefix,
            COUNT(*) as idx_count
        FROM sqlite_master 
        WHERE type='index' AND name LIKE 'idx_%'
        GROUP BY table_prefix
        ORDER BY idx_count DESC
        LIMIT 20
    """)
    
    print("\nIndexes by table:")
    for table, count in cursor.fetchall():
        print(f"  {table:30} {count:2} indexes")
    
    cursor.close()


def main():
    """Run performance benchmarks."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 1
    
    conn = sqlite3.connect(str(db_path))
    
    print("=" * 80)
    print("DATABASE PERFORMANCE BENCHMARK")
    print("=" * 80)
    
    # Generate test data
    generate_test_data(conn)
    
    # Show index statistics
    show_index_stats(conn)
    
    # Run benchmarks
    results = run_benchmarks(conn)
    
    # Summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    
    valid_results = [t for t in results.values() if t > 0]
    if valid_results:
        avg_time = sum(valid_results) / len(valid_results)
        max_time = max(valid_results)
        min_time = min(valid_results)
        
        print(f"\nAverage query time: {avg_time:.3f} ms")
        print(f"Fastest query:      {min_time:.3f} ms")
        print(f"Slowest query:      {max_time:.3f} ms")
        
        if avg_time < 2.0:
            print("\n✅ Excellent performance! All queries sub-2ms average.")
        elif avg_time < 5.0:
            print("\n✅ Good performance! All queries sub-5ms average.")
        else:
            print("\n⚠️  Some queries may benefit from additional optimization.")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit(main())

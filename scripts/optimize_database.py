#!/usr/bin/env python3
"""
Database Optimization Script for CV-Mindcare

This script applies performance optimizations to the SQLite database:
- Enables WAL (Write-Ahead Logging) mode for better concurrency
- Optimizes cache settings
- Analyzes tables for query optimization
- Vacuums the database to reclaim space

Usage:
    python scripts/optimize_database.py
"""

import sqlite3
import os
import sys
from contextlib import closing

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database import DB_PATH


def optimize_database(db_path: str = DB_PATH):
    """
    Apply performance optimizations to SQLite database.
    
    Args:
        db_path: Path to database file
    """
    print(f"Optimizing database: {db_path}")
    
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency
        print("Enabling WAL mode...")
        cursor.execute("PRAGMA journal_mode=WAL")
        result = cursor.fetchone()[0]
        print(f"  Journal mode: {result}")
        
        # Optimize synchronous mode
        print("Setting synchronous mode to NORMAL...")
        cursor.execute("PRAGMA synchronous=NORMAL")
        
        # Increase cache size (10MB = 10000 pages of 1KB)
        print("Setting cache size to 10MB...")
        cursor.execute("PRAGMA cache_size=10000")
        
        # Use memory for temporary storage
        print("Setting temp_store to MEMORY...")
        cursor.execute("PRAGMA temp_store=MEMORY")
        
        # Enable auto-vacuum
        print("Enabling auto-vacuum...")
        cursor.execute("PRAGMA auto_vacuum=FULL")
        
        # Analyze tables for query optimization
        print("Analyzing tables...")
        cursor.execute("ANALYZE")
        
        # Vacuum database to reclaim space and optimize
        print("Vacuuming database...")
        cursor.execute("VACUUM")
        
        conn.commit()
    
    print("\nDatabase optimization complete!")
    print("\nCurrent database settings:")
    
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        
        # Show current settings
        settings = [
            "journal_mode",
            "synchronous",
            "cache_size",
            "temp_store",
            "auto_vacuum",
        ]
        
        for setting in settings:
            cursor.execute(f"PRAGMA {setting}")
            value = cursor.fetchone()[0]
            print(f"  {setting}: {value}")
    
    # Get database size
    db_size = os.path.getsize(db_path) / 1024  # KB
    print(f"\nDatabase size: {db_size:.2f} KB")
    
    # Get table statistics
    print("\nTable statistics:")
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        
        tables = ["sensor_data", "face_detection", "sound_analysis", "air_quality"]
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} rows")


if __name__ == "__main__":
    optimize_database()

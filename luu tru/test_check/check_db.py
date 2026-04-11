"""Script to check database"""
import sqlite3
import os

db_file = "trading_bot.db"

if os.path.exists(db_file):
    print(f"Database file exists: {db_file}")
    print(f"Size: {os.path.getsize(db_file)} bytes")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\nTables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    Rows: {count}")
    
    conn.close()
else:
    print(f"Database file does not exist: {db_file}")


#!/usr/bin/env python
"""
Migration script to add new columns to bot_status table
Run this ONCE after updating the BotStatus model
"""

from sqlalchemy import text, inspect
from app.database import engine, SessionLocal
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_columns_to_bot_status():
    """Add missing columns to bot_status table"""
    
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("Migration: Add new columns to bot_status table")
        print("="*60 + "\n")
        
        columns_to_add = {
            'status': "VARCHAR(20) DEFAULT 'Idle'",
            'last_updated': "TIMESTAMP WITH TIME ZONE DEFAULT NULL",
            'consecutive_errors': "INTEGER DEFAULT 0"
        }
        
        # Check and add each column
        for column_name, column_def in columns_to_add.items():
            if column_exists('bot_status', column_name):
                print(f"✓ Column '{column_name}' already exists")
            else:
                print(f"✗ Column '{column_name}' missing - adding...")
                
                # Generate ALTER TABLE statement based on database type
                alter_sql = f"ALTER TABLE bot_status ADD COLUMN {column_name} {column_def}"
                
                print(f"  Executing: {alter_sql}")
                db.execute(text(alter_sql))
                db.commit()
                
                print(f"  ✓ Column '{column_name}' added successfully")
        
        print("\n" + "="*60)
        print("✓ Migration completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during migration: {e}\n")
        db.rollback()
        
        # Show manual SQL commands for reference
        print("\n" + "="*60)
        print("If automatic migration failed, run these SQL commands manually:")
        print("="*60 + "\n")
        
        for column_name, column_def in columns_to_add.items():
            if not column_exists('bot_status', column_name):
                sql = f"ALTER TABLE bot_status ADD COLUMN {column_name} {column_def};"
                print(sql)
        
        print("\n" + "="*60 + "\n")
        raise
        
    finally:
        db.close()


if __name__ == "__main__":
    add_columns_to_bot_status()

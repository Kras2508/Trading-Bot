"""
Script to add ip_whitelist column to bot_configs table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_add_ip_whitelist():
    """Add ip_whitelist column to bot_configs table"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL, echo=False)
        
        with engine.connect() as conn:
            # Check if column already exists
            if 'mssql' in settings.DATABASE_URL.lower():
                # SQL Server
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'bot_configs' 
                    AND COLUMN_NAME = 'ip_whitelist'
                """))
                exists = result.fetchone()[0] > 0
            else:
                # SQLite/PostgreSQL
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'bot_configs' 
                    AND COLUMN_NAME = 'ip_whitelist'
                """))
                exists = result.fetchone()[0] > 0
            
            if exists:
                logger.info("Column 'ip_whitelist' already exists. Skipping migration.")
                return
            
            # Add column
            if 'mssql' in settings.DATABASE_URL.lower():
                # SQL Server
                conn.execute(text("""
                    ALTER TABLE bot_configs
                    ADD ip_whitelist NVARCHAR(MAX) NULL
                """))
            else:
                # SQLite/PostgreSQL
                conn.execute(text("""
                    ALTER TABLE bot_configs
                    ADD COLUMN ip_whitelist TEXT NULL
                """))
            
            conn.commit()
            logger.info("✅ Successfully added 'ip_whitelist' column to bot_configs table")
            
    except Exception as e:
        logger.error(f"❌ Error adding ip_whitelist column: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add ip_whitelist column to bot_configs")
    print("=" * 60)
    migrate_add_ip_whitelist()
    print("Migration completed!")


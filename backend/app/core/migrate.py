"""
Database Migration Script
Runs automatically on app startup to update database schema
"""

import os
import logging

logger = logging.getLogger(__name__)

def run_migrations() -> bool:
    """
    Run database migrations using psycopg2 directly.
    """
    try:
        import psycopg2
        print("=" * 50)
        print("🔧 RUNNING DATABASE MIGRATIONS...")
        print("=" * 50)
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        print(f"📡 DATABASE_URL found: {bool(database_url)}")
        
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        # Convert Railway DB URL format if needed
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgres://", 1)
        
        print(f"🔗 Connecting to database...")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"✅ Database connected!")
        
        # Drop old constraint - we're now using String instead of Enum
        try:
            print(f"🔨 Dropping category constraint (using String type now)...")
            cur.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_category")
            print("✅ Dropped category constraint - categories are now free-form strings")
        except Exception as e:
            print(f"⚠️ Could not drop constraint: {e}")
        
        print(f"✅ Database migrations completed!")
        print("=" * 50)
        
        cur.close()
        conn.close()
        return True
        
    except ImportError as e:
        print(f"❌ psycopg2 not installed: {e}")
        print("⚠️ Skipping migrations, app may fail on category validation")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {type(e).__name__}: {e}")
        print("⚠️ Continuing without migrations")
        return False

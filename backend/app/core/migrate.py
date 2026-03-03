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
        
        # Drop ALL enum constraints - we're using String types now
        try:
            print(f"🔨 Dropping all enum constraints...")
            # Tasks constraints
            cur.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_category")
            cur.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_priority")
            cur.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_status")
            # Events constraints
            cur.execute("ALTER TABLE events DROP CONSTRAINT IF EXISTS valid_category")
            cur.execute("ALTER TABLE events DROP CONSTRAINT IF EXISTS valid_recurrence")
            print("✅ Dropped all constraints - columns are now free-form strings")
        except Exception as e:
            print(f"⚠️ Could not drop constraints: {e}")
        
        # Change column types to VARCHAR (in case they were ENUM)
        try:
            print(f"🔨 Converting columns to VARCHAR...")
            # Tasks
            cur.execute("ALTER TABLE tasks ALTER COLUMN category TYPE VARCHAR(100)")
            cur.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE VARCHAR(50)")
            cur.execute("ALTER TABLE tasks ALTER COLUMN status TYPE VARCHAR(50)")
            # Events
            cur.execute("ALTER TABLE events ALTER COLUMN category TYPE VARCHAR(50)")
            cur.execute("ALTER TABLE events ALTER COLUMN recurrence_type TYPE VARCHAR(50)")
            print("✅ Converted columns to VARCHAR")
        except Exception as e:
            print(f"⚠️ Could not convert columns: {e}")
        
        print(f"✅ Database migrations completed!")
        print("=" * 50)
        
        cur.close()
        conn.close()
        return True
        
    except ImportError as e:
        print(f"❌ psycopg2 not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {type(e).__name__}: {e}")
        return False

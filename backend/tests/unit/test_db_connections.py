#!/usr/bin/env python3
"""
Test all database connections
Run this after docker-compose up to verify everything is working
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_postgresql():
    """Test PostgreSQL/TimescaleDB connection"""
    try:
        import psycopg2
        from app.core.config import settings

        # Parse connection string
        conn_str = settings.DATABASE_URL.replace('postgresql://', '')
        user_pass, host_db = conn_str.split('@')
        user, password = user_pass.split(':')
        host_port, database = host_db.split('/')
        host, port = host_port.split(':')

        print("Testing PostgreSQL/TimescaleDB connection...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cur = conn.cursor()

        # Test basic query
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ PostgreSQL connected: {version[:50]}...")

        # Test TimescaleDB
        cur.execute("SELECT default_version FROM pg_available_extensions WHERE name = 'timescaledb';")
        ts_version = cur.fetchone()
        if ts_version:
            print(f"✅ TimescaleDB available: {ts_version[0]}")
        else:
            print("⚠️  TimescaleDB extension not found")

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection"""
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        from app.core.config import settings

        print("\nTesting MongoDB connection...")
        client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)

        # Force connection
        client.admin.command('ping')

        # Get database info
        db_list = client.list_database_names()
        print(f"✅ MongoDB connected")
        print(f"   Available databases: {', '.join(db_list)}")

        client.close()
        return True
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB connection failed (timeout): {e}")
        return False
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    try:
        import redis
        from app.core.config import settings

        print("\nTesting Redis connection...")
        r = redis.from_url(settings.REDIS_URL)

        # Test ping
        r.ping()
        print("✅ Redis connected")

        # Test set/get
        r.set('test_key', 'test_value', ex=10)
        value = r.get('test_key')
        if value == b'test_value':
            print("✅ Redis read/write test passed")

        # Get info
        info = r.info()
        print(f"   Redis version: {info['redis_version']}")
        print(f"   Memory used: {info['used_memory_human']}")

        r.close()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("=" * 60)
    print("Database Connection Tests")
    print("=" * 60)

    results = {
        'PostgreSQL': test_postgresql(),
        'MongoDB': test_mongodb(),
        'Redis': test_redis()
    }

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for db, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{db:20} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All database connections successful!")
        return 0
    else:
        print("\n⚠️  Some connections failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

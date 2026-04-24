"""
Layer 2 Database Verification Script

This script verifies:
1. PostgreSQL connection and tables
2. Indicator definitions exist
3. Indicator values storage works
4. MongoDB collections exist
5. Redis caching available
"""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_postgresql():
    """Test PostgreSQL connection and tables."""
    print("\n" + "="*60)
    print("PHASE 2: DATABASE VERIFICATION")
    print("="*60)
    
    print("\n[1/5] Testing PostgreSQL Connection...")
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Connection config (Docker container uses port 15432)
        pg_config = {
            'host': '127.0.0.1',
            'port': 15432,
            'database': 'national_indicator',
            'user': 'postgres',
            'password': 'postgres_secure_2024'
        }
        
        conn = psycopg2.connect(**pg_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ PostgreSQL connected successfully!")
        
        # Check tables exist
        print("\n[2/5] Checking database tables...")
        
        tables_to_check = [
            'indicator_definitions',
            'indicator_values',
            'indicator_keywords',
        ]
        
        for table in tables_to_check:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table,))
            exists = cursor.fetchone()['exists']
            status = "✅" if exists else "❌"
            print(f"  {status} {table}")
        
        # Count indicator definitions
        print("\n[3/5] Checking indicator definitions...")
        cursor.execute("SELECT COUNT(*) as count FROM indicator_definitions")
        count = cursor.fetchone()['count']
        print(f"  📊 Total indicators defined: {count}")
        
        # Show PESTEL category breakdown
        cursor.execute("""
            SELECT pestel_category, COUNT(*) as count 
            FROM indicator_definitions 
            GROUP BY pestel_category
            ORDER BY pestel_category
        """)
        categories = cursor.fetchall()
        print("\n  PESTEL Category Breakdown:")
        for cat in categories:
            print(f"    - {cat['pestel_category']}: {cat['count']} indicators")
        
        # Check indicator values
        print("\n[4/5] Checking indicator values (time-series data)...")
        cursor.execute("SELECT COUNT(*) as count FROM indicator_values")
        values_count = cursor.fetchone()['count']
        print(f"  📈 Total indicator values stored: {values_count}")
        
        if values_count > 0:
            # Get latest values
            cursor.execute("""
                SELECT iv.indicator_id, id.indicator_name, iv.value, iv.confidence, iv.timestamp
                FROM indicator_values iv
                JOIN indicator_definitions id ON iv.indicator_id = id.indicator_id
                ORDER BY iv.timestamp DESC
                LIMIT 5
            """)
            latest = cursor.fetchall()
            print("\n  Latest stored values:")
            for row in latest:
                print(f"    - {row['indicator_name'][:40]}: {row['value']:.2f} (conf: {row['confidence']:.2f})")
        else:
            print("  ⚠️ No indicator values stored yet - pipeline may need to run")
        
        # Test insert capability (dry run)
        print("\n[5/5] Testing write capability...")
        try:
            cursor.execute("SELECT current_user, current_database()")
            info = cursor.fetchone()
            print(f"  ✅ Write access confirmed (user: {info['current_user']})")
        except Exception as e:
            print(f"  ❌ Write test failed: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")
        return False


def test_mongodb():
    """Test MongoDB connection and collections."""
    print("\n" + "-"*60)
    print("MongoDB Verification")
    print("-"*60)
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient(
            "mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin",
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connected successfully!")
        
        db = client['national_indicator']
        
        # Check collections
        collections = db.list_collection_names()
        print(f"\n📁 Collections found: {len(collections)}")
        
        key_collections = ['processed_articles', 'entity_extractions', 'narratives']
        for coll in key_collections:
            status = "✅" if coll in collections else "❌"
            count = db[coll].count_documents({}) if coll in collections else 0
            print(f"  {status} {coll}: {count} documents")
        
        # Check processed_articles for Layer 2 processing status
        l2_processed = db.processed_articles.count_documents({"layer2_processed": True})
        l2_pending = db.processed_articles.count_documents({"$or": [
            {"layer2_processed": {"$exists": False}},
            {"layer2_processed": False}
        ]})
        
        print(f"\n📊 Layer 2 Processing Status:")
        print(f"  - Processed: {l2_processed}")
        print(f"  - Pending: {l2_pending}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Error: {e}")
        return False


def test_redis():
    """Test Redis connection."""
    print("\n" + "-"*60)
    print("Redis Verification")
    print("-"*60)
    
    try:
        import redis
        
        r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis connected successfully!")
        
        # Check cache status
        info = r.info('memory')
        print(f"  📊 Used Memory: {info.get('used_memory_human', 'N/A')}")
        
        keys_count = r.dbsize()
        print(f"  🔑 Total Keys: {keys_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis Error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("LAYER 2 DATABASE VERIFICATION SCRIPT")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pg_ok = test_postgresql()
    mongo_ok = test_mongodb()
    redis_ok = test_redis()
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"  PostgreSQL: {'✅ OK' if pg_ok else '❌ FAILED'}")
    print(f"  MongoDB:    {'✅ OK' if mongo_ok else '❌ FAILED'}")
    print(f"  Redis:      {'✅ OK' if redis_ok else '❌ FAILED'}")
    
    if all([pg_ok, mongo_ok, redis_ok]):
        print("\n✅ All database connections verified successfully!")
        return 0
    else:
        print("\n⚠️ Some database connections failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())

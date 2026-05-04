import sys
import os
import json
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import redis

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def test_day1_setup():
    print("🚀 Starting Day 1 Integration Test...")
    
    # 1. Check Mock Data
    print("\n📂 Checking Mock Data...")
    mock_dir = os.path.join(os.path.dirname(__file__), "../mock_data")
    expected_files = [
        "articles_political.json",
        "articles_economic.json",
        "articles_social.json",
        "articles_environmental.json",
        "articles_mixed.json"
    ]
    
    all_files_exist = True
    total_articles = 0
    
    if not os.path.exists(mock_dir):
        print(f"❌ Mock data directory not found: {mock_dir}")
        all_files_exist = False
    else:
        for filename in expected_files:
            filepath = os.path.join(mock_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    count = len(data)
                    total_articles += count
                    print(f"   ✅ Found {filename} ({count} articles)")
            else:
                print(f"   ❌ Missing {filename}")
                all_files_exist = False
                
    if all_files_exist and total_articles >= 200:
        print(f"✅ Mock Data Check Passed! Total articles: {total_articles}")
    else:
        print("❌ Mock Data Check Failed!")

    # 2. Check Database Connections (Optional - requires Docker running)
    print("\n🔌 Checking Database Connections (Skipping if services not running)...")
    
    # Postgres
    try:
        # Using default credentials from docker-compose
        pg_url = "postgresql://postgres:postgres@localhost:5432/national_indicator"
        engine = create_engine(pg_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ PostgreSQL/TimescaleDB Connected")
    except Exception as e:
        print(f"   ⚠️ PostgreSQL Connection Failed: {e}")

    # MongoDB
    try:
        mongo_client = MongoClient("mongodb://localhost:27017/")
        mongo_client.admin.command('ping')
        print("   ✅ MongoDB Connected")
    except Exception as e:
        print(f"   ⚠️ MongoDB Connection Failed: {e}")

    # Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("   ✅ Redis Connected")
    except Exception as e:
        print(f"   ⚠️ Redis Connection Failed: {e}")

    print("\n🎉 Day 1 Setup Verification Complete!")

if __name__ == "__main__":
    test_day1_setup()

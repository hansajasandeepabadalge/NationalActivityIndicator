"""Detailed connection test"""
import psycopg2
import os

print("=" * 70)
print("DETAILED POSTGRESQL CONNECTION TEST")
print("=" * 70)

# Test 1: Try with connection string
print("\n[TEST 1] Connecting with connection string...")
try:
    conn = psycopg2.connect("postgresql://postgres:postgres_secure_2024@127.0.0.1:5432/national_indicator")
    print("✅ SUCCESS with connection string!")
    conn.close()
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 2: Try with DSN parameters and PGPASSWORD env
print("\n[TEST 2] Connecting with PGPASSWORD environment variable...")
os.environ['PGPASSWORD'] = 'postgres_secure_2024'
try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='national_indicator'
    )
    print("✅ SUCCESS with PGPASSWORD!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   PostgreSQL: {version[:60]}...")
    cursor.execute("SELECT current_database();")
    print(f"   Database: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    print(f"   Tables: {cursor.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "=" * 70)

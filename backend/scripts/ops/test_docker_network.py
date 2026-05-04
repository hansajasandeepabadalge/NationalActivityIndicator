#!/usr/bin/env python3
"""Test database connection from Docker network"""
import psycopg2

print("Testing PostgreSQL connection via Docker network...")
try:
    conn = psycopg2.connect(
        "postgresql://postgres:postgres_secure_2024@national_indicator_timescaledb:5432/national_indicator"
    )
    print("✅ SUCCESS: Connected to PostgreSQL via Docker network!")

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"PostgreSQL version: {version[:80]}")

    cursor.execute("SELECT current_database();")
    print(f"Current database: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    table_count = cursor.fetchone()[0]
    print(f"Tables in public schema: {table_count}")

    conn.close()
    print("\n✅ Connection test PASSED!")

except Exception as e:
    print(f"❌ Connection FAILED: {e}")
    exit(1)

"""Test database connection"""
import psycopg2
import os

# Try different connection methods
print("Testing PostgreSQL connection...")
print("=" * 60)

passwords = ['postgres_secure_2024', 'postgres', '']
hosts = ['127.0.0.1', 'localhost']

for host in hosts:
    for password in passwords:
        try:
            if password:
                conn = psycopg2.connect(
                    host=host,
                    port=5432,
                    user='postgres',
                    password=password,
                    database='national_indicator'
                )
            else:
                conn = psycopg2.connect(
                    host=host,
                    port=5432,
                    user='postgres',
                    database='national_indicator'
                )

            print(f"✅ SUCCESS with host={host}, password={'<empty>' if not password else password}")
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            print(f"   PostgreSQL version: {cursor.fetchone()[0][:50]}...")
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            print(f"   Tables in public schema: {cursor.fetchone()[0]}")
            conn.close()
            break
        except Exception as e:
            print(f"❌ Failed with host={host}, password={'<empty>' if not password else password}: {str(e)[:80]}")
    else:
        continue
    break
else:
    print("\n❌ All connection attempts failed!")

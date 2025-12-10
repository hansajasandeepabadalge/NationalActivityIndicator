"""Check PostgreSQL enum types and table structure."""

import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=15432,
    dbname='national_indicator',
    user='postgres',
    password='postgres_secure_2024'
)

cur = conn.cursor()

# Check enum types
print("=" * 60)
print("Enum Types in Database")
print("=" * 60)

cur.execute("""
    SELECT t.typname, e.enumlabel
    FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    ORDER BY t.typname, e.enumsortorder
""")

types = {}
for typname, label in cur.fetchall():
    if typname not in types:
        types[typname] = []
    types[typname].append(label)

for typname, labels in types.items():
    print(f"\n{typname}:")
    for label in labels:
        print(f"  - {label}")

# Check column types for indicator_definitions
print("\n" + "=" * 60)
print("Column Types for indicator_definitions")
print("=" * 60)

cur.execute("""
    SELECT column_name, data_type, udt_name
    FROM information_schema.columns 
    WHERE table_name='indicator_definitions'
    ORDER BY ordinal_position
""")
for col, dtype, udt in cur.fetchall():
    print(f"  {col}: {dtype} (udt: {udt})")

cur.close()
conn.close()

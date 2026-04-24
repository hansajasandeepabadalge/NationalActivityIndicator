"""Check current indicator definitions in PostgreSQL."""

import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=15432,
    dbname='national_indicator',
    user='postgres',
    password='postgres_secure_2024'
)

cur = conn.cursor()

# Check table columns
print("=" * 60)
print("Table Structure: indicator_definitions")
print("=" * 60)

cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='indicator_definitions'
    ORDER BY ordinal_position
""")
for col, dtype in cur.fetchall():
    print(f"  {col}: {dtype}")

# Check current indicators
print("\n" + "=" * 60)
print("Current Indicators")
print("=" * 60)

cur.execute("SELECT * FROM indicator_definitions ORDER BY pestel_category")
rows = cur.fetchall()
print(f"Total indicators: {len(rows)}")

if rows:
    # Get column names
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='indicator_definitions'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cur.fetchall()]
    
    for row in rows:
        data = dict(zip(cols, row))
        cat = data.get('pestel_category', 'N/A')
        name = data.get('indicator_name', 'N/A')
        subcat = data.get('subcategory', 'N/A')
        print(f"  {cat}: {name} ({subcat})")

cur.close()
conn.close()

"""Create article_indicator_mappings table directly"""
import psycopg2
from psycopg2 import sql

# Connection parameters matching Docker
conn_params = {
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'national_indicator',
    'user': 'postgres',
    'password': 'postgres_secure_2024'
}

conn = None
cursor = None

try:
    print("Connecting to database...")
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    print("Creating article_indicator_mappings table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_indicator_mappings (
            mapping_id SERIAL PRIMARY KEY,
            article_id VARCHAR(100) NOT NULL,
            indicator_id VARCHAR(50) NOT NULL,
            match_confidence FLOAT NOT NULL,
            classification_method VARCHAR(50) DEFAULT 'rule_based',
            matched_keywords TEXT[],
            keyword_match_count INTEGER DEFAULT 0,
            article_category VARCHAR(50),
            article_published_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            extra_metadata JSONB,
            FOREIGN KEY (indicator_id) REFERENCES indicator_definitions(indicator_id) ON DELETE CASCADE
        );
    """)

    print("Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_mappings_article ON article_indicator_mappings(article_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_mappings_indicator ON article_indicator_mappings(indicator_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_mappings_confidence ON article_indicator_mappings(match_confidence);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_mappings_method ON article_indicator_mappings(classification_method);")

    conn.commit()
    print("✅ Table and indexes created successfully!")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM article_indicator_mappings;")
    count = cursor.fetchone()[0]
    print(f"✅ Table exists with {count} rows")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

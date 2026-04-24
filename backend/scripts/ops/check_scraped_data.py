"""
Check scraped data in database

Verifies what data has been stored from the enhanced scraping system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.agent_models import SourceConfig
from sqlalchemy import text


def check_database():
    """Check what's in the database."""

    print("="*80)
    print("🔍 DATABASE CHECK - Scraped Articles")
    print("="*80)

    db = SessionLocal()

    try:
        # Check source configs
        print("\n📊 Source Configurations:")
        print("-"*80)

        sources = db.query(SourceConfig).filter(SourceConfig.is_active == True).all()
        by_type = {}
        for source in sources:
            stype = source.source_type or "unknown"
            by_type[stype] = by_type.get(stype, 0) + 1

        print(f"Total active sources: {len(sources)}")
        for stype, count in sorted(by_type.items()):
            print(f"  - {stype.title()}: {count}")

        print(f"\n📰 Source List:")
        for source in sources[:10]:  # Show first 10
            display = (source.config_metadata or {}).get('display_name', source.source_name)
            print(f"  ✅ {source.source_name:<25} {display}")

        if len(sources) > 10:
            print(f"  ... and {len(sources) - 10} more sources")

        # Check for processed articles table
        print(f"\n💾 Checking for processed articles...")
        try:
            result = db.execute(text("""
                SELECT
                    table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE '%article%'
            """))

            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"✅ Found article tables:")
                for table in tables:
                    print(f"   - {table}")

                    # Count records
                    try:
                        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.fetchone()[0]
                        print(f"     Records: {count}")

                        if count > 0:
                            # Show recent records
                            sample_result = db.execute(text(f"""
                                SELECT * FROM {table}
                                ORDER BY created_at DESC
                                LIMIT 3
                            """))

                            print(f"     Recent records:")
                            for i, row in enumerate(sample_result.fetchall(), 1):
                                print(f"       [{i}] {dict(row)}")

                    except Exception as e:
                        print(f"     Could not query: {e}")
            else:
                print(f"⚠️  No article tables found")

        except Exception as e:
            print(f"❌ Error checking tables: {e}")

        # Check raw article storage
        print(f"\n📝 Checking for raw articles...")
        try:
            result = db.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE '%raw%'
            """))

            raw_tables = [row[0] for row in result.fetchall()]
            if raw_tables:
                print(f"✅ Found raw tables: {', '.join(raw_tables)}")
            else:
                print(f"⚠️  No raw article tables found")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n" + "="*80)
        print("Database check complete")
        print("="*80)

    finally:
        db.close()


if __name__ == "__main__":
    check_database()

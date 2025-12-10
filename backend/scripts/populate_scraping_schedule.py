"""
Populate Scraping Schedule Table

This script populates the scraping_schedule table with configurations
for all news sources that the AI agents will manage.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 15432,
    'database': 'national_indicator',
    'user': 'postgres',
    'password': 'postgres_secure_2024'
}

# Source configurations
# Priority levels: CRITICAL (5min), HIGH (15min), MEDIUM (30min), LOW (60min)
SOURCES = [
    {
        'source_name': 'ada_derana',
        'source_url': 'https://www.adaderana.lk',
        'frequency_minutes': 5,
        'priority_level': 'critical',
        'is_active': True,
        'reliability_score': 0.95,
        'updated_by': 'system_init'
    },
    {
        'source_name': 'daily_ft',
        'source_url': 'https://www.ft.lk',
        'frequency_minutes': 15,
        'priority_level': 'high',
        'is_active': True,
        'reliability_score': 0.90,
        'updated_by': 'system_init'
    },
    {
        'source_name': 'hiru_news',
        'source_url': 'https://www.hirunews.lk',
        'frequency_minutes': 15,
        'priority_level': 'high',
        'is_active': True,
        'reliability_score': 0.88,
        'updated_by': 'system_init'
    },
    {
        'source_name': 'newsfirst',
        'source_url': 'https://www.newsfirst.lk',
        'frequency_minutes': 20,
        'priority_level': 'high',
        'is_active': True,
        'reliability_score': 0.85,
        'updated_by': 'system_init'
    },
    {
        'source_name': 'lankadeepa',
        'source_url': 'https://www.lankadeepa.lk',
        'frequency_minutes': 30,
        'priority_level': 'medium',
        'is_active': True,
        'reliability_score': 0.82,
        'updated_by': 'system_init'
    },
    {
        'source_name': 'divaina',
        'source_url': 'https://www.divaina.com',
        'frequency_minutes': 30,
        'priority_level': 'medium',
        'is_active': True,
        'reliability_score': 0.80,
        'updated_by': 'system_init'
    },
    {
        'source_name': 'tamilmirror',
        'source_url': 'https://www.tamilmirror.lk',
        'frequency_minutes': 45,
        'priority_level': 'medium',
        'is_active': True,
        'reliability_score': 0.78,
        'updated_by': 'system_init'
    },
    {
        'source_name': 'sunday_times',
        'source_url': 'https://www.sundaytimes.lk',
        'frequency_minutes': 60,
        'priority_level': 'low',
        'is_active': True,
        'reliability_score': 0.85,
        'updated_by': 'system_init'
    }
]


def populate_scraping_schedule():
    """Populate the scraping_schedule table with source configurations."""
    
    print("=" * 60)
    print("POPULATING SCRAPING SCHEDULE TABLE")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'scraping_schedule'
            );
        """)
        table_exists = cursor.fetchone()['exists']
        
        if not table_exists:
            print("❌ ERROR: scraping_schedule table does not exist!")
            print("   Please run migrations first:")
            print("   alembic upgrade head")
            return False
        
        print(f"\n✅ Table 'scraping_schedule' exists")
        
        # Check current entries
        cursor.execute("SELECT COUNT(*) as count FROM scraping_schedule")
        current_count = cursor.fetchone()['count']
        print(f"   Current entries: {current_count}")
        
        # Insert or update sources
        inserted = 0
        updated = 0
        
        for source in SOURCES:
            # Check if source already exists
            cursor.execute(
                "SELECT id FROM scraping_schedule WHERE source_name = %s",
                (source['source_name'],)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute("""
                    UPDATE scraping_schedule 
                    SET source_url = %s,
                        frequency_minutes = %s,
                        priority_level = %s,
                        is_active = %s,
                        reliability_score = %s,
                        updated_by = %s,
                        updated_at = %s
                    WHERE source_name = %s
                """, (
                    source['source_url'],
                    source['frequency_minutes'],
                    source['priority_level'],
                    source['is_active'],
                    source['reliability_score'],
                    source['updated_by'],
                    datetime.utcnow(),
                    source['source_name']
                ))
                updated += 1
                print(f"   📝 Updated: {source['source_name']}")
            else:
                # Insert new entry
                cursor.execute("""
                    INSERT INTO scraping_schedule 
                    (source_name, source_url, frequency_minutes, priority_level, 
                     is_active, reliability_score, updated_by, created_at, updated_at,
                     last_articles_count, consecutive_failures, total_articles_scraped,
                     avg_articles_per_scrape)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    source['source_name'],
                    source['source_url'],
                    source['frequency_minutes'],
                    source['priority_level'],
                    source['is_active'],
                    source['reliability_score'],
                    source['updated_by'],
                    datetime.utcnow(),
                    datetime.utcnow(),
                    0,  # last_articles_count
                    0,  # consecutive_failures
                    0,  # total_articles_scraped
                    0.0  # avg_articles_per_scrape
                ))
                inserted += 1
                print(f"   ✅ Inserted: {source['source_name']}")
        
        conn.commit()
        
        # Verify final state
        cursor.execute("""
            SELECT source_name, source_url, frequency_minutes, priority_level, 
                   is_active, reliability_score, updated_by
            FROM scraping_schedule
            ORDER BY frequency_minutes ASC
        """)
        entries = cursor.fetchall()
        
        print(f"\n" + "=" * 60)
        print("SCRAPING SCHEDULE SUMMARY")
        print("=" * 60)
        print(f"{'Source':<20} {'Priority':<10} {'Freq':<8} {'Active':<8} {'Reliability'}")
        print("-" * 60)
        
        for entry in entries:
            print(f"{entry['source_name']:<20} {entry['priority_level']:<10} {entry['frequency_minutes']:<8} "
                  f"{'Yes' if entry['is_active'] else 'No':<8} {entry['reliability_score']:.2f}")
        
        print("-" * 60)
        print(f"\nTotal: {len(entries)} sources configured")
        print(f"  - Inserted: {inserted}")
        print(f"  - Updated: {updated}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Scraping schedule populated successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = populate_scraping_schedule()
    sys.exit(0 if success else 1)

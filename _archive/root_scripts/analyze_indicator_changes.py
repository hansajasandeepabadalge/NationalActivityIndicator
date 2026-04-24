"""
Analyze top 5 indicators with largest changes and identify causing articles
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from datetime import datetime, timedelta
import json

print("="*60)
print("TOP 5 INDICATORS WITH LARGEST CHANGES")
print("="*60)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='127.0.0.1',
    port=15432,
    database='national_indicator',
    user='postgres',
    password='postgres_secure_2024'
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Get indicators with historical data to calculate changes
cursor.execute("""
    WITH latest_values AS (
        SELECT DISTINCT ON (indicator_id)
            indicator_id,
            indicator_name,
            value as current_value,
            confidence,
            timestamp as current_time
        FROM indicator_values
        ORDER BY indicator_id, timestamp DESC
    ),
    previous_values AS (
        SELECT DISTINCT ON (indicator_id)
            indicator_id,
            value as previous_value,
            timestamp as previous_time
        FROM indicator_values
        WHERE timestamp < (SELECT MAX(timestamp) - INTERVAL '1 day' FROM indicator_values)
        ORDER BY indicator_id, timestamp DESC
    )
    SELECT 
        l.indicator_id,
        l.indicator_name,
        l.current_value,
        p.previous_value,
        l.current_value - COALESCE(p.previous_value, l.current_value) as change,
        ABS(l.current_value - COALESCE(p.previous_value, l.current_value)) as abs_change,
        l.confidence,
        l.current_time
    FROM latest_values l
    LEFT JOIN previous_values p ON l.indicator_id = p.indicator_id
    WHERE l.current_value IS NOT NULL
    ORDER BY abs_change DESC
    LIMIT 5
""")

top_indicators = cursor.fetchall()

# Connect to MongoDB for article details
mongo_client = MongoClient('mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin')
db = mongo_client['national_indicator']

print("\n")
for i, ind in enumerate(top_indicators, 1):
    print(f"\n{'='*60}")
    print(f"#{i}. {ind['indicator_name']}")
    print(f"{'='*60}")
    print(f"Current Value: {ind['current_value']:.2f}")
    print(f"Previous Value: {ind['previous_value']:.2f if ind['previous_value'] else 'N/A'}")
    print(f"Change: {ind['change']:+.2f} ({abs(ind['change']):.2f} absolute)")
    print(f"Confidence: {ind['confidence']:.2f}")
    
    # Get matching articles from latest calculation
    recent_calcs = list(db.indicator_calculations.find({
        'indicator_id': ind['indicator_id'],
        'timestamp': {'$gte': datetime.now() - timedelta(hours=2)}
    }).sort('timestamp', -1).limit(1))
    
    if recent_calcs and 'matching_articles' in recent_calcs[0]:
        article_ids = recent_calcs[0]['matching_articles'][:5]
        print(f"\nArticles Contributing to This Indicator ({len(article_ids)} total):")
        
        # Get article details
        articles = list(db.processed_articles.find({
            'article_id': {'$in': article_ids}
        }).limit(5))
        
        for j, article in enumerate(articles, 1):
            print(f"\n  Article {j}:")
            print(f"    Title: {article.get('title', 'N/A')[:80]}...")
            print(f"    Source: {article.get('source', 'N/A')}")
            print(f"    Published: {article.get('published_at', 'N/A')}")
            pestel = article.get('pestel_categories', [])
            if pestel:
                print(f"    Categories: {', '.join(pestel[:3])}")
    else:
        print("\n  No recent article data found")

cursor.close()
conn.close()
mongo_client.close()

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)

"""
Show highest and lowest indicator values with contributing articles
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from datetime import datetime, timedelta

print("="*70)
print("CURRENT INDICATOR VALUES - HIGHEST & LOWEST")
print("="*70)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='127.0.0.1',
    port=15432,
    database='national_indicator',
    user='postgres',
    password='postgres_secure_2024'
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Get latest indicator values
cursor.execute("""
    SELECT DISTINCT ON (indicator_id)
        indicator_id,
        name,
        value,
        confidence,
        article_count,
        timestamp
    FROM indicator_values
    ORDER BY indicator_id, timestamp DESC
""")

all_indicators = cursor.fetchall()

# Sort by value
sorted_indicators = sorted(all_indicators, key=lambda x: x['value'], reverse=True)

# Connect to MongoDB
mongo_client = MongoClient('mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin')
db = mongo_client['national_indicator']

def show_indicator_details(indicator, rank_type):
    print(f"\n{'='*70}")
    print(f"{rank_type}: {indicator['name']}")
    print(f"{'='*70}")
    print(f"Value: {indicator['value']:.2f}/100")
    print(f"Confidence: {indicator['confidence']:.2f}")
    print(f"Article Count: {indicator['article_count']}")
    print(f"Last Updated: {indicator['timestamp']}")
    
    # Get matching articles
    recent_calc = db.indicator_calculations.find_one({
        'indicator_id': indicator['indicator_id']
    }, sort=[('timestamp', -1)])
    
    if recent_calc and 'matching_articles' in recent_calc:
        article_ids = recent_calc['matching_articles'][:3]  # Top 3 articles
        print(f"\nTop Contributing Articles ({len(recent_calc['matching_articles'])} total):")
        
        articles = list(db.processed_articles.find({
            'article_id': {'$in': article_ids}
        }))
        
        for i, article in enumerate(articles, 1):
            print(f"\n  [{i}] {article.get('title', 'N/A')[:70]}")
            print(f"      Source: {article.get('source', 'N/A')}")
            if 'published_at' in article:
                print(f"      Published: {article['published_at']}")
            pestel = article.get('pestel_categories', [])
            if pestel:
                print(f"      Categories: {', '.join(pestel[:2])}")
            # Show snippet if available
            body = article.get('body', '')
            if body:
                snippet = body[:150].replace('\n', ' ')
                print(f"      Snippet: {snippet}...")
    else:
        print("\n  No article data available")

# Show TOP 5 HIGHEST
print("\n\n" + "🔥"*35)
print("TOP 5 HIGHEST INDICATORS")
print("🔥"*35)

for i, ind in enumerate(sorted_indicators[:5], 1):
    show_indicator_details(ind, f"#{i} HIGHEST")

# Show TOP 5 LOWEST
print("\n\n" + "📉"*35)
print("TOP 5 LOWEST INDICATORS")
print("📉"*35)

for i, ind in enumerate(sorted_indicators[-5:][::-1], 1):
    show_indicator_details(ind, f"#{i} LOWEST")

print("\n" + "="*70)
print(f"TOTAL INDICATORS ANALYZED: {len(all_indicators)}")
print("="*70)

cursor.close()
conn.close()
mongo_client.close()

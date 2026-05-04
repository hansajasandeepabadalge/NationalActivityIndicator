"""
Show highest and lowest indicator values with contributing articles (MongoDB only)
"""
from pymongo import MongoClient
from datetime import datetime, timedelta

print("="*70)
print("CURRENT INDICATOR VALUES - HIGHEST & LOWEST")
print("="*70)

# Connect to MongoDB
mongo_client = MongoClient('mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin')
db = mongo_client['national_indicator']

# Get latest indicator calculations
recent_time = datetime.now() - timedelta(hours=2)
indicators = list(db.indicator_calculations.find({
    'timestamp': {'$gte': recent_time}
}).sort('timestamp', -1))

# Group by indicator_id to get latest for each
latest_indicators = {}
for ind in indicators:
    ind_id = ind.get('indicator_id')
    if ind_id and ind_id not in latest_indicators:
        latest_indicators[ind_id] = ind

# Convert to list and sort by value
indicator_list = list(latest_indicators.values())
sorted_by_value = sorted(indicator_list, key=lambda x: x.get('value', 0), reverse=True)

print(f"\nTotal Indicators Found: {len(sorted_by_value)}")

def show_indicator(ind, rank_type):
    print(f"\n{'='*70}")
    print(f"{rank_type}: {ind.get('indicator_name', 'Unknown')}")
    print(f"{'='*70}")
    print(f"Value: {ind.get('value', 0):.2f}/100")
    print(f"Confidence: {ind.get('confidence', 0):.2f}")
    print(f"Article Count: {ind.get('article_count', 0)}")
    print(f"Category: {ind.get('pestel_category', 'N/A')}")
    print(f"Subcategory: {ind.get('subcategory', 'N/A')}")
    
    # Get matching articles
    article_ids = ind.get('matching_articles', [])[:3]
    if article_ids:
        print(f"\nTop Contributing Articles ({len(ind.get('matching_articles', []))} total):")
        
        articles = list(db.processed_articles.find({
            'article_id': {'$in': article_ids}
        }))
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'N/A')
            print(f"\n  [{i}] {title[:75]}")
            print(f"      Source: {article.get('source', 'N/A')}")
            
            pub_date = article.get('published_at', 'N/A')
            if pub_date != 'N/A':
                print(f"      Published: {pub_date}")
            
            pestel = article.get('pestel_categories', [])
            if pestel:
                print(f"      Categories: {', '.join(pestel[:3])}")
            
            # Show snippet
            body = article.get('body', '')
            if body:
                snippet = body[:120].replace('\n', ' ').strip()
                print(f"      Snippet: {snippet}...")
    else:
        print("\n  No article data available")

# Show TOP 5 HIGHEST
print("\n\n" + "🔥"*35)
print("TOP 5 HIGHEST INDICATORS")
print("🔥"*35)

for i, ind in enumerate(sorted_by_value[:5], 1):
    show_indicator(ind, f"#{i} HIGHEST")

# Show TOP 5 LOWEST
print("\n\n" + "📉"*35)
print("TOP 5 LOWEST INDICATORS")
print("📉"*35)

for i, ind in enumerate(reversed(sorted_by_value[-5:]), 1):
    show_indicator(ind, f"#{i} LOWEST")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)

mongo_client.close()

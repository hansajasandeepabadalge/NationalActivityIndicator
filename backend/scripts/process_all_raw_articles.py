"""
Process ALL Raw Articles through Cleaning Pipeline

This script:
1. Fetches ALL raw articles from MongoDB
2. Cleans and processes each article
3. Stores in processed_articles collection
4. Handles various article formats gracefully
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv
load_dotenv()


async def process_all_articles():
    print("=" * 60)
    print(" PROCESSING ALL RAW ARTICLES")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    mongo_url = 'mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    
    try:
        await client.admin.command('ping')
        print("\n✅ Connected to MongoDB")
    except Exception as e:
        print(f"\n❌ Failed to connect: {e}")
        return
    
    db = client.national_indicator
    
    # Import the cleaner
    try:
        from app.cleaning.cleaner import DataCleaner
        from app.models.raw_article import RawArticle
        from app.models.processed_article import ProcessedArticle
        cleaner = DataCleaner()
        print("✅ DataCleaner loaded")
    except Exception as e:
        print(f"❌ Failed to load cleaner: {e}")
        client.close()
        return
    
    # Get counts
    raw_count = await db.raw_articles.count_documents({})
    already_processed = await db.processed_articles.count_documents({})
    
    print(f"\n📊 Current Status:")
    print(f"   Raw articles: {raw_count}")
    print(f"   Already processed: {already_processed}")
    
    # Get all raw articles
    print(f"\n🔄 Processing all raw articles...")
    
    cursor = db.raw_articles.find({})
    raw_articles = await cursor.to_list(length=None)
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, doc in enumerate(raw_articles):
        article_id = doc.get('article_id', str(doc.get('_id')))
        
        try:
            # Check if already processed
            existing = await db.processed_articles.find_one({'article_id': article_id})
            if existing:
                skipped_count += 1
                continue
            
            # Ensure required fields exist
            if 'scrape_metadata' not in doc:
                doc['scrape_metadata'] = {
                    'job_id': 0,
                    'scraped_at': doc.get('created_at', datetime.utcnow()),
                    'scraper_version': '1.0.0'
                }
            else:
                if 'job_id' not in doc['scrape_metadata']:
                    doc['scrape_metadata']['job_id'] = 0
                if 'scraper_version' not in doc['scrape_metadata']:
                    doc['scrape_metadata']['scraper_version'] = '1.0.0'
            
            # Create RawArticle
            raw_article = RawArticle(**doc)
            
            # Process through cleaner
            processed = cleaner.process_article(raw_article)
            
            # Add source info to processed article
            processed.source_name = doc.get('source', {}).get('name', '')
            processed.source_url = doc.get('source', {}).get('url', '')
            processed.scraped_at = doc.get('scrape_metadata', {}).get('scraped_at')
            
            # Store in MongoDB
            processed_dict = processed.model_dump(mode='json')
            await db.processed_articles.update_one(
                {'article_id': article_id},
                {'$set': processed_dict},
                upsert=True
            )
            
            success_count += 1
            
            # Progress update every 20 articles
            if (i + 1) % 20 == 0:
                print(f"   Processed {i + 1}/{len(raw_articles)} articles...")
                
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Only show first 5 errors
                print(f"   ⚠️ Error processing {article_id}: {e}")
    
    # Final counts
    final_processed = await db.processed_articles.count_documents({})
    
    print(f"\n📊 Processing Complete:")
    print(f"   Newly processed: {success_count}")
    print(f"   Skipped (already done): {skipped_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total in processed_articles: {final_processed}")
    
    client.close()
    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(process_all_articles())

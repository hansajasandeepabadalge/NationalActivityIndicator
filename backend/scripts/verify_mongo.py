import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.mongodb import mongodb
from app.models.raw_article import RawArticle, SourceInfo, ScrapeMetadata, RawContent, ValidationStatus

async def test_mongo_connection():
    print("Testing MongoDB Connection...")
    try:
        mongodb.connect()
        db = mongodb.get_database()
        print(f"Connected to database: {db.name}")
        
        # Test inserting a document
        collection = db['raw_articles']
        
        article = RawArticle(
            article_id="test_article_001",
            source=SourceInfo(source_id=1, name="Test Source", url="http://test.com"),
            scrape_metadata=ScrapeMetadata(job_id=1, scraped_at=datetime.utcnow(), scraper_version="1.0"),
            raw_content=RawContent(title="Test Title", body="This is a test body."),
            validation=ValidationStatus(is_valid=True)
        )
        
        # Convert to dict and insert (using by_alias=True if we had aliases, but we don't really)
        article_dict = article.model_dump(mode='json')
        
        # Upsert
        result = await collection.update_one(
            {"article_id": article.article_id},
            {"$set": article_dict},
            upsert=True
        )
        
        print(f"Upserted document. Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted ID: {result.upserted_id}")
        
        # Retrieve
        saved_doc = await collection.find_one({"article_id": "test_article_001"})
        print(f"Retrieved document: {saved_doc['raw_content']['title']}")
        
        print("MongoDB Connection and Operation Successful!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mongodb.close()

if __name__ == "__main__":
    asyncio.run(test_mongo_connection())

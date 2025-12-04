import asyncio
import sys
import os
import logging

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.mongodb import mongodb
from app.models.raw_article import RawArticle
from app.cleaning.cleaner import DataCleaner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_cleaning():
    print("Initializing MongoDB...")
    mongodb.connect()
    
    try:
        db = mongodb.get_database()
        raw_collection = db['raw_articles']
        processed_collection = db['processed_articles']
        
        cleaner = DataCleaner()
        
        # Fetch all raw articles
        cursor = raw_collection.find({})
        articles_to_process = await cursor.to_list(length=None)
        
        print(f"Found {len(articles_to_process)} raw articles to clean.")
        
        count = 0
        for doc in articles_to_process:
            try:
                # Convert dict to RawArticle model
                # MongoDB stores datetime as datetime, Pydantic expects it.
                # But sometimes it might be string if not parsed correctly.
                # Let's rely on Pydantic's parsing.
                raw_article = RawArticle(**doc)
                
                # Process
                processed_article = cleaner.process_article(raw_article)
                
                # Save
                processed_dict = processed_article.model_dump(mode='json')
                
                await processed_collection.update_one(
                    {"article_id": processed_article.article_id},
                    {"$set": processed_dict},
                    upsert=True
                )
                count += 1
            except Exception as e:
                logger.error(f"Error processing article {doc.get('article_id')}: {e}")
                
        print(f"Successfully cleaned and saved {count} articles.")
        
    except Exception as e:
        print(f"Error running cleaning pipeline: {e}")
    finally:
        mongodb.close()

if __name__ == "__main__":
    asyncio.run(run_cleaning())

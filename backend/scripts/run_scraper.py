import asyncio
import sys
import os
import logging

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.mongodb import mongodb
from app.scrapers.news.ada_derana import AdaDeranaScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_scraper():
    print("Initializing MongoDB...")
    mongodb.connect()
    
    try:
        scraper = AdaDeranaScraper()
        print(f"Running scraper: {scraper.source_info.name}")
        
        articles = await scraper.run()
        
        if not articles:
            print("No articles found.")
            return

        print(f"Saving {len(articles)} articles to MongoDB...")
        db = mongodb.get_database()
        collection = db['raw_articles']
        
        new_count = 0
        updated_count = 0
        for article in articles:
            article_dict = article.model_dump(mode='json')
            result = await collection.update_one(
                {"article_id": article.article_id},
                {"$set": article_dict},
                upsert=True
            )
            if result.upserted_id:
                new_count += 1
            elif result.modified_count > 0:
                updated_count += 1
                
        print(f"Summary: {new_count} new articles, {updated_count} updated articles.")
        
    except Exception as e:
        print(f"Error running scraper: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mongodb.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())

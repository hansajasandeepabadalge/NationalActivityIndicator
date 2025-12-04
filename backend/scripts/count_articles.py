import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.mongodb import mongodb

async def count_articles():
    mongodb.connect()
    try:
        db = mongodb.get_database()
        count = await db.raw_articles.count_documents({})
        print(f"Total articles in DB: {count}")
    finally:
        mongodb.close()

if __name__ == "__main__":
    asyncio.run(count_articles())

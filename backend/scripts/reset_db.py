import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.mongodb import mongodb

async def reset_database():
    print("Connecting to MongoDB...")
    mongodb.connect()
    
    try:
        db = mongodb.get_database()
        db_name = db.name
        print(f"Dropping database: {db_name}")
        
        await mongodb.client.drop_database(db_name)
        print("Database dropped successfully.")
        
    except Exception as e:
        print(f"Error dropping database: {e}")
    finally:
        mongodb.close()

if __name__ == "__main__":
    asyncio.run(reset_database())

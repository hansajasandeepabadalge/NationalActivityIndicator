"""MongoDB connection management"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None

    def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    def get_database(self):
        """Get database instance"""
        return self.client.national_indicator

    def get_collection(self, name: str):
        """Get collection by name"""
        db = self.get_database()
        return db[name]

# Singleton instance
mongodb = MongoDB()

def get_mongodb():
    """Dependency for getting MongoDB instance"""
    return mongodb.get_database()

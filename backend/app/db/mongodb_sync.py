"""
Synchronous MongoDB connection management
Use this for Layer 2 processing tasks that require sync access
"""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDBSync:
    """
    Synchronous MongoDB client for Layer 2 data processing
    Use this for batch processing, ML training, and other sync operations
    """

    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None

    def connect(self):
        """Connect to MongoDB using synchronous client"""
        try:
            self.client = MongoClient(
                settings.MONGODB_URL,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client.national_indicator
            logger.info("Synchronous MongoDB client connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect synchronous MongoDB client: {e}")
            raise

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Synchronous MongoDB client closed")

    def get_database(self) -> Database:
        """Get database instance"""
        if not self.db:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.db

    def get_collection(self, name: str) -> Collection:
        """Get collection by name"""
        db = self.get_database()
        return db[name]

    # Layer 2 specific collections
    def get_indicator_calculations(self) -> Collection:
        """Get indicator calculations collection"""
        return self.get_collection('indicator_calculations')

    def get_indicator_narratives(self) -> Collection:
        """Get indicator narratives collection"""
        return self.get_collection('indicator_narratives')

    def get_entity_extractions(self) -> Collection:
        """Get entity extractions collection"""
        return self.get_collection('entity_extractions')

    def get_ml_training_data(self) -> Collection:
        """Get ML training data collection"""
        return self.get_collection('ml_training_data')

    def get_raw_articles(self) -> Collection:
        """Get raw articles collection"""
        return self.get_collection('raw_articles')

    def get_processed_content(self) -> Collection:
        """Get processed content collection"""
        return self.get_collection('processed_content')


# Singleton instance
mongodb_sync = MongoDBSync()


def get_mongodb_sync() -> Database:
    """Dependency for getting synchronous MongoDB instance"""
    return mongodb_sync.get_database()

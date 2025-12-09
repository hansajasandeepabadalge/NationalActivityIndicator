from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from loguru import logger

from app.core.config import settings


class Database:

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")

            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )

            cls.db = cls.client[settings.MONGODB_DB_NAME]

            # Import models here to avoid circular imports
            from app.models.user import User
            from app.models.company import Company
            from app.models.Indicator import NationalIndicator, OperationalIndicatorValue
            from app.models.insight import BusinessInsight
            from app.models.access_log import DashboardAccessLog

            # Initialize Beanie with document models
            await init_beanie(
                database=cls.db,
                document_models=[
                    User,
                    Company,
                    NationalIndicator,
                    OperationalIndicatorValue,
                    BusinessInsight,
                    DashboardAccessLog
                ]
            )

            # Verify connection
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def disconnect(cls) -> None:
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.db

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls.client is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.client


# Convenience functions
async def connect_to_mongo() -> None:
    await Database.connect()


async def close_mongo_connection() -> None:
    await Database.disconnect()


def get_database() -> AsyncIOMotorDatabase:
    return Database.get_db()
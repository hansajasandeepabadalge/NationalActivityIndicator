"""Redis connection management"""
import redis.asyncio as aioredis
from redis import Redis
from app.core.config import settings

class RedisClient:
    client: aioredis.Redis = None

    def connect(self):
        """Connect to Redis"""
        self.client = aioredis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )

    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()

    def get_client(self):
        """Get Redis client"""
        return self.client

# Singleton instance
redis_client = RedisClient()

def get_redis():
    """Dependency for getting Redis client"""
    return redis_client.get_client()

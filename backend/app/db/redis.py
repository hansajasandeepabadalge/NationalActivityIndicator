import json
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class RedisCache:

    client: Optional[redis.Redis] = None

    @classmethod
    async def connect(cls) -> None:
        try:
            logger.info(f"Connecting to Redis at {settings.REDIS_URL}")
            cls.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Verify connection
            await cls.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Caching will be disabled.")
            cls.client = None

    @classmethod
    async def disconnect(cls) -> None:
        if cls.client:
            await cls.client.close()
            logger.info("Disconnected from Redis")

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        if cls.client is None:
            return None

        try:
            value = await cls.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis GET error: {e}")
            return None

    @classmethod
    async def set(
            cls,
            key: str,
            value: Any,
            ttl: Optional[int] = None
    ) -> bool:
        if cls.client is None:
            return False

        try:
            ttl = ttl or settings.REDIS_CACHE_TTL
            await cls.client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.warning(f"Redis SET error: {e}")
            return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        if cls.client is None:
            return False

        try:
            await cls.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE error: {e}")
            return False

    @classmethod
    async def delete_pattern(cls, pattern: str) -> int:
        if cls.client is None:
            return 0

        try:
            keys = []
            async for key in cls.client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await cls.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis DELETE PATTERN error: {e}")
            return 0

    @classmethod
    async def exists(cls, key: str) -> bool:
        if cls.client is None:
            return False

        try:
            return await cls.client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Redis EXISTS error: {e}")
            return False


def cache_key(*args: str) -> str:
    return ":".join(str(arg) for arg in args)


# Convenience functions
async def connect_to_redis() -> None:
    await RedisCache.connect()


async def close_redis_connection() -> None:
    await RedisCache.disconnect()
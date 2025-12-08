"""Database module for MongoDB and Redis connections."""
from app.db.mongodb import (
    Database,
    connect_to_mongo,
    close_mongo_connection,
    get_database
)
from app.db.redis import (
    RedisCache,
    connect_to_redis,
    close_redis_connection,
    cache_key
)

__all__ = [
    "Database",
    "connect_to_mongo",
    "close_mongo_connection",
    "get_database",
    "RedisCache",
    "connect_to_redis",
    "close_redis_connection",
    "cache_key"
]
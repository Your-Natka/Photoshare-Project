import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


def get_redis_client():
    """
    Factory function for Redis client.
    Allows easy mocking in unit tests.
    """
    return redis.from_url(REDIS_URL)


redis_client = get_redis_client()
redis_cache = redis_client
redis = redis_client
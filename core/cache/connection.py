from redis import asyncio as aioredis
from redis.asyncio import Redis

from core.cache.base_types import RedisBase
from core.settings import get_settings

REDIS_CLIENT: dict[int, Redis] = None

SETTINGS = get_settings()


async def init_redis():
    global REDIS_CLIENT
    REDIS_CLIENT = dict()
    for base in RedisBase:
        pool = aioredis.ConnectionPool.from_url(
            SETTINGS.CACHE_URL,
            db=base,
            max_connections=10,
            decode_responses=True,
        )
        REDIS_CLIENT[base] = aioredis.Redis(connection_pool=pool)


async def close_redis():
    global REDIS_CLIENT
    for connection in REDIS_CLIENT.values():
        await connection.close(True)
    REDIS_CLIENT = None


def get_redis(base: int = RedisBase.DEFAULT) -> Redis:
    return REDIS_CLIENT[base]

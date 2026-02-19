import json
from redis.asyncio import Redis
from src.core.settings import settings

redis: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

DEFAULT_TTL = 60

async def cache_get(key: str):
    raw = await redis.get(key)
    return json.loads(raw) if raw else None

async def cache_set(key: str, value, ttl: int = DEFAULT_TTL):
    await redis.set(key, json.dumps(value), ex=ttl)

async def cache_delete(key: str):
    await redis.delete(key)

async def cache_delete_prefix(prefix: str):
    async for key in redis.scan_iter(match=f"{prefix}*"):
        await redis.delete(key)

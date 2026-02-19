import json
import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError
from src.core.settings import settings

logger = logging.getLogger(__name__)

DEFAULT_TTL = 60

redis: Redis | None = None
CACHE_ENABLED = False


async def init_cache() -> None:
    """
    Chame no startup do FastAPI. Se Redis não subir, a API continua sem cache.
    """
    global redis, CACHE_ENABLED

    try:
        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis.ping()
        CACHE_ENABLED = True
        logger.info("Redis conectado: cache habilitado")
    except Exception as e:
        redis = None
        CACHE_ENABLED = False
        logger.warning("Redis indisponível: cache desabilitado (%s)", e)


async def cache_get(key: str):
    if not CACHE_ENABLED or redis is None:
        return None
    try:
        raw = await redis.get(key)
        return json.loads(raw) if raw else None
    except (RedisError, json.JSONDecodeError) as e:
        logger.warning("cache_get falhou (key=%s): %s", key, e)
        return None


async def cache_set(key: str, value, ttl: int = DEFAULT_TTL):
    if not CACHE_ENABLED or redis is None:
        return
    try:
        await redis.set(key, json.dumps(value), ex=ttl)
    except RedisError as e:
        logger.warning("cache_set falhou (key=%s): %s", key, e)


async def cache_delete(key: str):
    if not CACHE_ENABLED or redis is None:
        return
    try:
        await redis.delete(key)
    except RedisError as e:
        logger.warning("cache_delete falhou (key=%s): %s", key, e)


async def cache_delete_prefix(prefix: str):
    if not CACHE_ENABLED or redis is None:
        return
    try:
        async for key in redis.scan_iter(match=f"{prefix}*"):
            await redis.delete(key)
    except RedisError as e:
        logger.warning("cache_delete_prefix falhou (prefix=%s): %s", prefix, e)

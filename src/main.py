import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.controllers.user_controller import router
from src.models.database import Base, engine
from src.core.settings import settings
import src.cache.redis_client as cache
from src.core.logging_config import setup_logging
from src.core.middlewares import RequestIdMiddleware

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(getattr(settings, "LOG_LEVEL", "INFO"))
    logger.info("app_starting", extra={"debug": getattr(settings, "APP_DEBUG", None)})

    try:
        await cache.init_cache()
        logger.info("redis_ready")
    except Exception:
        logger.exception("redis_unavailable")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("db_schema_ready")

    yield

    try:
        if cache.redis is not None:
            await cache.redis.close()
    except Exception:
        logger.exception("redis_close_failed")

    await engine.dispose()
    logger.info("app_stopped")


app = FastAPI(
    title="CRUD Usuários",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)
app.include_router(router)


@app.get("/health")
async def health():
    db_ok = False
    redis_ok = False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False

    try:
        if cache.CACHE_ENABLED and cache.redis is not None:
            redis_ok = bool(await cache.redis.ping())
    except Exception:
        redis_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "down",
        "redis": "ok" if redis_ok else ("disabled" if not cache.CACHE_ENABLED else "down"),
        "cache_enabled": cache.CACHE_ENABLED,
    }

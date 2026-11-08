import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
import src.cache.redis_client as cache
from src.controllers.user_controller import router
from src.core.logging_config import setup_logging
from src.core.middlewares import RequestIdMiddleware
from src.core.settings import settings
from src.models.database import engine

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.LOG_LEVEL)
    # O esquema é atualizado por Alembic antes do servidor.
    try:
        await cache.init_cache()
        yield
    finally:
        await cache.close_cache()
        await engine.dispose()


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan, debug=settings.APP_DEBUG)
app.add_middleware(RequestIdMiddleware)
app.include_router(router)


@app.get("/health")
async def health():
    """Prontidão: banco obrigatório; cache opcional."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    redis_ok = False
    try:
        if cache.CACHE_ENABLED and cache.redis is not None:
            redis_ok = bool(await cache.redis.ping())
    except Exception:
        pass
    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={
            "status": "ok" if db_ok else "degraded",
            "database": "ok" if db_ok else "down",
            "redis": "ok" if redis_ok else ("disabled" if not cache.CACHE_ENABLED else "down"),
            "cache_enabled": cache.CACHE_ENABLED,
        },
    )

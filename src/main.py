import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.controllers.user_controller import router
from src.models.database import Base, engine
from src.core.settings import settings
from src.cache.redis_client import init_cache
from src.core.logging_config import setup_logging
from src.core.middlewares import RequestIdMiddleware

logger = logging.getLogger("app")



@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(getattr(settings, "LOG_LEVEL", "INFO"))
    logger.info("app_starting", extra={"debug": getattr(settings, "APP_DEBUG", None)})

    try:
        await init_cache()
        logger.info("redis_ready")
    except Exception:
        logger.exception("redis_unavailable")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("db_schema_ready")

    yield

    await engine.dispose()
    logger.info("app_stopped")

app = FastAPI(
    title="CRUD Usuários",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(RequestIdMiddleware)

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}



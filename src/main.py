import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

# Router principal da API (endpoints de usuários)
from src.controllers.user_controller import router

# Engine e metadata do SQLAlchemy
from src.models.database import Base, engine

# Configurações da aplicação (env vars, etc.)
from src.core.settings import settings

# Importa o módulo de cache inteiro (IMPORTANTE para refletir CACHE_ENABLED atualizado)
import src.cache.redis_client as cache

# Configuração central de logging
from src.core.logging_config import setup_logging

# Middleware que adiciona request_id para rastreamento de requisições
from src.core.middlewares import RequestIdMiddleware


# Logger principal da aplicação
logger = logging.getLogger("app")


# =========================================================
# LIFESPAN DO FASTAPI (startup + shutdown controlado)
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executa quando a aplicação inicia e quando encerra.
    Ideal para:
    - configurar logging
    - conectar serviços externos (Redis, DB, etc.)
    - liberar recursos no shutdown
    """

    # Configura nível de log conforme settings
    setup_logging(getattr(settings, "LOG_LEVEL", "INFO"))

    # Log inicial da aplicação
    logger.info("app_starting", extra={"debug": getattr(settings, "APP_DEBUG", None)})

    # -----------------------------------------------------
    # Inicializa Redis (cache)
    # -----------------------------------------------------
    try:
        await cache.init_cache()
        logger.info("redis_ready")
    except Exception:
        # Não quebra a API se Redis falhar
        logger.exception("redis_unavailable")

    # -----------------------------------------------------
    # Garante que as tabelas do banco existam
    # (em produção ideal usar Alembic migrations)
    # -----------------------------------------------------
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("db_schema_ready")

    # -----------------------------------------------------
    # APLICAÇÃO ESTÁ PRONTA
    # -----------------------------------------------------
    yield

    # -----------------------------------------------------
    # SHUTDOWN CONTROLADO
    # -----------------------------------------------------

    # Fecha conexão com Redis
    try:
        if cache.redis is not None:
            await cache.redis.close()
    except Exception:
        logger.exception("redis_close_failed")

    # Fecha pool de conexões do banco
    await engine.dispose()

    logger.info("app_stopped")


# =========================================================
# CRIAÇÃO DA APLICAÇÃO FASTAPI
# =========================================================
app = FastAPI(
    title="CRUD Usuários",
    version="1.0.0",
    lifespan=lifespan,  # registra ciclo de vida
)

# Middleware que adiciona request_id em cada requisição
app.add_middleware(RequestIdMiddleware)

# Registra rotas do controller
app.include_router(router)


# =========================================================
# HEALTH CHECK (monitoramento da aplicação)
# =========================================================
@app.get("/health")
async def health():
    """
    Endpoint para monitoramento externo (Kubernetes, Docker, etc.)

    Verifica:
    - banco de dados
    - redis
    - status geral
    """

    db_ok = False
    redis_ok = False

    # -----------------------------------------------------
    # Testa conexão com banco
    # -----------------------------------------------------
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False

    # -----------------------------------------------------
    # Testa conexão com Redis
    # -----------------------------------------------------
    try:
        if cache.CACHE_ENABLED and cache.redis is not None:
            redis_ok = bool(await cache.redis.ping())
    except Exception:
        redis_ok = False

    # -----------------------------------------------------
    # Resposta padronizada de health
    # -----------------------------------------------------
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "down",
        "redis": "ok" if redis_ok else ("disabled" if not cache.CACHE_ENABLED else "down"),
        "cache_enabled": cache.CACHE_ENABLED,
    }

"""Autenticação de clientes de serviço; não representa login de usuários."""

from secrets import compare_digest
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from src.core.settings import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    expected = settings.API_KEY.get_secret_value().encode("utf-8")
    provided = (api_key or "").encode("utf-8")
    if not compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API ausente ou inválida",
            headers={"WWW-Authenticate": "APIKey"},
        )

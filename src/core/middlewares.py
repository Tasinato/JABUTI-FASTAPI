from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.request_context import request_id_ctx_var

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid4())
        request_id_ctx_var.set(rid)

        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
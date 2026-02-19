import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any
from src.core.request_context import get_request_id

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # contexto opcional
        payload["module"] = record.module
        payload["func"] = record.funcName
        payload["line"] = record.lineno

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        # request_id do contexto
        request_id = get_request_id()
        if request_id:  
            payload["request_id"] = request_id

        return json.dumps(payload, ensure_ascii=False)

def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    # evita handlers duplicados (uvicorn reload, etc.)
    root.handlers.clear()
    root.addHandler(handler)

    # (opcional) harmoniza logs do uvicorn/fastapi
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True
    
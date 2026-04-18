import json
import logging
import sys

from api.core.config import settings
from api.core.trace_context import trace_id_var


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "trace_id": trace_id_var.get(""),
                "module": record.module,
                "func": record.funcName,
            }
        )


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    if not any(isinstance(h.formatter, JSONFormatter) for h in root.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root.addHandler(handler)

    for name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "celery",
        "celery.worker",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

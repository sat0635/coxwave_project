import contextvars
import logging
import sys
import uuid

from loguru import logger

logging.getLogger("uvicorn.access").disabled = True

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "[{extra[request_id]}] <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
)

request_id_ctx_var = contextvars.ContextVar("request_id", default=None)


def generate_request_id():
    return f"req-{uuid.uuid4().hex[:6]}"


def get_logger():
    request_id = request_id_ctx_var.get()
    return logger.bind(request_id=request_id or "req-unknown")

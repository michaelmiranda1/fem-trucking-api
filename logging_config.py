import logging
from logging import Logger
from typing import Optional

from config import settings
from request_context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def setup_logging() -> Logger:
    logger = logging.getLogger("fem_api")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Avoid duplicate handlers on reload
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s %(levelname)s fem_api request_id=%(request_id)s %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        handler.addFilter(RequestIdFilter())
        logger.addHandler(handler)

    # Keep uvicorn logs reasonable
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    return logger


logger: Optional[Logger] = None
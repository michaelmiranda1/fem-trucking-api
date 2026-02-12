# utils/logger.py
from __future__ import annotations

import logging
from typing import Any, Dict

from utils.request_context import get_request_id


class RequestLogger(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: Dict[str, Any]):
        extra = kwargs.get("extra", {})
        extra.setdefault("request_id", get_request_id())
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(name: str) -> RequestLogger:
    base = logging.getLogger(name)
    return RequestLogger(base, {})
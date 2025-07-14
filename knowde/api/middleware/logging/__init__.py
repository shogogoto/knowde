"""fastapiログ用."""

import logging
import time
import uuid
from typing import override

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from knowde.config.env import Settings

from .context import request_id_var
from .log_config import setup_logging

s = Settings()
setup_logging()


class LoggingMiddleware(BaseHTTPMiddleware):
    """ログ用."""

    @override
    async def dispatch(self, request: Request, call_next):
        # Set request_id to context
        req_id = str(uuid.uuid4())
        request_id_var.set(req_id)

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Set headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-Id"] = req_id

        # Get logger and log details
        logger = logging.getLogger(__name__)
        logger.info(
            f"Successfully called API in {process_time:.4f}s",  # noqa: G004
            extra={
                "status_code": response.status_code,
                "service": str(request.url),
                "method": request.method,
                "process_time": process_time,
            },
        )

        # Clear context var
        request_id_var.set(None)
        return response

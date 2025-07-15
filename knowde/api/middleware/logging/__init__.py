"""fastapiログ用."""

import logging
import time
import uuid
from typing import override

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from knowde.feature.user.backend import get_strategy
from knowde.feature.user.manager import get_user_manager

from .context import method_var, request_id_var, url_var, user_id_var


async def req2user_id(request: Request) -> str | None:  # noqa: D103
    jwt: str | None = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        jwt = auth_header.split(" ")[1]
    else:
        jwt = request.cookies.get("fastapiusersauth")

    if jwt:
        user = await get_strategy().read_token(jwt, get_user_manager())
        if user:
            return user.id
    return None


class LoggingMiddleware(BaseHTTPMiddleware):
    """ログ用."""

    @override
    async def dispatch(self, request, call_next):
        # Set request_id to context
        req_id = str(uuid.uuid4())
        url_path = request.url.path
        method = request.method
        user_id = await req2user_id(request)
        rid_token = request_id_var.set(req_id)
        url_token = url_var.set(url_path)
        method_token = method_var.set(method)
        user_id_token = user_id_var.set(user_id)
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time

            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-Id"] = req_id
            response.headers["X-URL"] = url_path
            if user_id:
                response.headers["X-User-Id"] = user_id

            logger = logging.getLogger(__name__)
            logger.info("Success in %.4fs", process_time)
            return response
        finally:
            request_id_var.reset(rid_token)
            url_var.reset(url_token)
            method_var.reset(method_token)
            user_id_var.reset(user_id_token)

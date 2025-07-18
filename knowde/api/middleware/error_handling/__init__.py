"""fastapi error handling middleware."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """fastapiでエラーを検出."""

    @override
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        try:
            return await call_next(request)
        except HTTPException as e:
            if await request.is_disconnected():
                return JSONResponse(
                    status_code=e.status_code,
                    content=e.detail,
                )
            return JSONResponse(
                status_code=e.status_code,
                content=e.detail,
                headers=e.headers,
            )
        except Exception as e:
            logger.exception("Uncaught exception %s", e.__class__.__name__)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=e.args,
            )

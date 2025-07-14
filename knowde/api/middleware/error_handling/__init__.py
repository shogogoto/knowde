"""fastapi error handling middleware."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


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

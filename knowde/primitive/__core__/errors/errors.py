"""errorの基礎."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """fastapiでエラーを検出."""

    async def dispatch(  # noqa: D102
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        try:
            res: Response = await call_next(request)
        except DomainError as e:
            return JSONResponse(
                status_code=e.status_code,
                content=e.detail,
            )

        return res


class DomainError(Exception):
    """ドメイン関連エラー."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    msg: str = "domain error"
    headers: dict[str, str] | None = None

    @property
    def detail(self) -> dict[str, Any]:
        """詳細."""
        return {
            "detail": {
                "code": self.status_code,
                "message": self.msg,
            },
        }

    def __init__(  # noqa: D107
        self,
        msg: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        if msg is not None:
            self.msg = msg
        self.headers = headers

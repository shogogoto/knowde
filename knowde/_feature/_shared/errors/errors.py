from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
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
    status_code: int
    msg: str = "domain error"
    headers: dict[str, str] | None = None

    @property
    def detail(self) -> dict[str, Any]:
        return {
            "detail": {
                "code": self.status_code,
                "message": self.msg,
            },
        }

    def __init__(
        self,
        msg: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        if msg is not None:
            self.msg = msg
        self.headers = headers

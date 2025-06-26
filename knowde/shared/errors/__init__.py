"""共通エラー."""

from typing import Any

from fastapi import HTTPException, status


class DomainError(HTTPException):
    """ドメイン関連エラー."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    msg: str = "domain error"
    headers: dict[str, str] | None = None

    @property
    def detail(self) -> dict[str, Any]:
        """詳細."""
        return {
            "code": self.status_code,
            "message": self.msg,
        }

    def __init__(  # noqa: D107
        self,
        msg: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        if msg is not None:
            self.msg = msg
        self.headers = headers

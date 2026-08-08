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


class NotExistsAccessError(DomainError):
    """存在しないのにアクセス."""

    status_code = status.HTTP_404_NOT_FOUND


class CompleteNotFoundError(DomainError):
    """補完時に見つからない."""

    status_code = status.HTTP_404_NOT_FOUND


class NotUniqueError(DomainError):
    """1つが見つかるべきとき."""

    status_code = status.HTTP_409_CONFLICT


class NotFoundError(DomainError):
    """Neomodel内で見つからなかったとき."""

    status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsError(DomainError):
    """既に作成済み."""

    status_code = status.HTTP_409_CONFLICT

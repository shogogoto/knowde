"""auth errors."""

from fastapi import status

from knowde.shared.errors import DomainError


class TokenUnsavedError(Exception):
    """認証用トークンが保存されていない."""


class UserNotFoundError(DomainError):
    """ユーザーが見つからない."""

    status_code = status.HTTP_404_NOT_FOUND


class UserNotUniqueError(DomainError):
    """ユーザーが複数見つかった."""

    status_code = status.HTTP_409_CONFLICT

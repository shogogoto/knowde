"""definition repo errors."""

from fastapi import status

from knowde.primitive.__core__.errors.errors import DomainError


class UndefinedMarkedTermError(Exception):
    """説明文中のマークに対応する用語が未定義だった."""


class AlreadyDefinedError(DomainError):
    """定義済み."""

    status_code = status.HTTP_409_CONFLICT


class DuplicateDefinedError(DomainError):
    """１つの用語に複数定義."""

    status_code = status.HTTP_409_CONFLICT

"""folder errors."""

from fastapi import status

from knowde.shared.errors import DomainError


class EntryAlreadyExistsError(Exception):
    """既にフォルダ or リソースあるやんけ."""


class EntryNotFoundError(Exception):
    """フォルダが見つからない."""


class SaveResourceError(Exception):
    """リソースの保存に失敗した."""


class DuplicatedTitleError(Exception):
    """同一タイトルは1つだけ."""


class NotOwnerError(DomainError):
    """所有者ではない."""

    status_code = status.HTTP_403_FORBIDDEN

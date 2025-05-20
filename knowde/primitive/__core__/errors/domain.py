"""共通エラー."""

from fastapi import status

from knowde.primitive.__core__.errors.errors import DomainError


class NotExistsAccessError(DomainError):
    """存在しないのにアクセス."""

    status_code = status.HTTP_404_NOT_FOUND


class CompleteNotFoundError(DomainError):
    """補完時に見つからない."""

    status_code = status.HTTP_404_NOT_FOUND


class MultiHitError(DomainError):
    """１つが見つかるべきとき."""

    status_code = status.HTTP_409_CONFLICT


class NotFoundError(DomainError):
    """neomodel内で見つからなかったとき."""

    status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsError(DomainError):
    """既に作成済み."""

    status_code = status.HTTP_409_CONFLICT

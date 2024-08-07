from fastapi import status

from knowde._feature._shared.errors.errors import DomainError


class NotExistsAccessError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class CompleteNotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class MultiHitError(DomainError):
    status_code = status.HTTP_409_CONFLICT


class NeomodelNotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsError(DomainError):
    status_code = status.HTTP_409_CONFLICT

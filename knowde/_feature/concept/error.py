"""concept error."""
from fastapi import status

from knowde._feature._shared import DomainError


class NotExistsUidAccessError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class CompleteNotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class CompleteMultiHitError(DomainError):
    status_code = status.HTTP_409_CONFLICT

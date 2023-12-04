from fastapi import status

from knowde._feature._shared.errors.errors import DomainError


class NotExistsUidAccessError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND

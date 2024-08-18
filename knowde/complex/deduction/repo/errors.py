"""error."""
from fastapi import status

from knowde._feature._shared.errors.errors import DomainError


class CyclicDependencyError(DomainError):
    """前提と同じ結論."""

    status_code: int = status.HTTP_409_CONFLICT


class PremiseDuplicationError(DomainError):
    """前提の重複."""

    status_code: int = status.HTTP_409_CONFLICT


class NoPremiseError(DomainError):
    """前提がない."""

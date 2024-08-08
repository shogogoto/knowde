from knowde._feature._shared.errors.errors import DomainError


class MonthRangeError(DomainError):
    """月が[1, 12]外."""


class DayRangeError(DomainError):
    """日が[1, 31]外."""


class InvalidTimeYMDError(DomainError):
    """不正な組YMD."""

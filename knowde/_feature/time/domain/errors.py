from knowde._feature._shared.errors.errors import DomainError


class MonthRangeError(DomainError):
    """月が[1, 12]外."""


class DayRangeError(DomainError):
    """日が[1, 31]外."""


class InvalidTimeYMDError(DomainError):
    """不正な組YMD."""


class EndBeforeStartError(DomainError):
    """開始の前に終わる."""


class NotEqualTimelineError(DomainError):
    """時系列名が異なる."""


class EmptyPeriodError(DomainError):
    """空の期間."""

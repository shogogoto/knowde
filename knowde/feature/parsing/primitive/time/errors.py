"""error."""


class EndBeforeStartError(Exception):
    """期間が不正."""


class ParseWhenError(Exception):
    """期間の表現が不正."""

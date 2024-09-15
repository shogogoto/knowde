"""parse errors."""


class SourceMatchError(Exception):
    """ソースが特定できない."""


class NameConflictError(Exception):
    """名前衝突."""

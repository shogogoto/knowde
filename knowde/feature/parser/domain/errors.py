"""parse errors."""


class SourceMatchError(Exception):
    """ソースが特定できない."""


class TermConflictError(Exception):
    """名前衝突."""


class NameMismatchError(Exception):
    """nameの値が見つからないはずがない."""


class ContextMismatchError(Exception):
    """未定義の文脈DA!."""

"""parse errors."""


class NameMismatchError(Exception):
    """nameの値が見つからないはずがない."""


class ContextMismatchError(Exception):
    """未定義の文脈DA!."""

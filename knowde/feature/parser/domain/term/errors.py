"""term errors."""


class TermMergeError(Exception):
    """用語の合併を許さないのに."""


class TermConflictError(Exception):
    """用語の衝突."""

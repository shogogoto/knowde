"""term errors."""


class TermMergeError(Exception):
    """用語の合併を許さないのに."""


class TermConflictError(Exception):
    """用語の衝突."""


class AliasContainsMarkError(Exception):
    """別名にマークを含んだらダメ."""


class TermResolveError(Exception):
    """用語解決に失敗."""

"""term errors."""


class TermError(Exception):
    """用語系エラー."""


class TermMergeError(TermError):
    """用語の合併を許さないのに."""


class TermConflictError(TermError):
    """用語の衝突."""


class AliasContainsMarkError(TermError):
    """別名にマークを含んだらダメ."""


class TermResolveError(TermError):
    """用語解決に失敗."""


class MarkUncontainedError(TermError):
    """マークが用語解決器に含まれない."""

"""term errors."""


class TermMergeError(Exception):
    """用語の合併を許さないのに."""


class TermConflictError(Exception):
    """用語の衝突."""


class AliasContainsMarkError(Exception):
    """別名にマークを含んだらダメ."""


class MarkContainsMarkError(Exception):
    """マーク内にマークを含む."""


class EmptyMarkError(Exception):
    """mark内が空."""


class PlaceHolderMappingError(Exception):
    """プレースホルダーを置換するための対応づけに失敗."""

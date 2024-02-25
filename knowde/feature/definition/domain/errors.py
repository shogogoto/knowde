class MarkContainsMarkError(Exception):
    """マーク内にマークを含む."""


class EmptyMarkError(Exception):
    """mark内が空."""


class PlaceHolderMappingError(Exception):
    """プレースホルダーを置換するための対応づけに失敗."""

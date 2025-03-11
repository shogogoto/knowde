"""folder errors."""


class EntryAlreadyExistsError(Exception):
    """既にフォルダ or リソースあるやんけ."""


class EntryNotFoundError(Exception):
    """フォルダが見つからない."""

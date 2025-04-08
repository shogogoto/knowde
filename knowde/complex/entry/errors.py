"""folder errors."""


class EntryAlreadyExistsError(Exception):
    """既にフォルダ or リソースあるやんけ."""


class EntryNotFoundError(Exception):
    """フォルダが見つからない."""


class SaveResourceError(Exception):
    """リソースの保存に失敗した."""


class DuplicatedTitleError(Exception):
    """同一タイトルは1つだけ."""

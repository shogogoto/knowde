"""folder errors."""


class SubFolderCreateError(Exception):
    """サブフォルダ作成エラー."""


class FolderAlreadyExistsError(Exception):
    """既にフォルダあるやんけ."""


class FolderNotFoundError(Exception):
    """フォルダが見つからない."""

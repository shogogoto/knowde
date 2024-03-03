"""definition repo errors."""


class UndefinedMarkedTermError(Exception):
    """説明文中のマークに対応する用語が未定義だった."""


class AlreadyDefinedError(Exception):
    """定義済み."""

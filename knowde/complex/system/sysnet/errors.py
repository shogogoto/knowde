"""系エラー."""


class UnResolvedTermError(Exception):
    """用語解決がまだ."""


class SysNetNotFoundError(Exception):
    """ネットワークに含まれないノード."""

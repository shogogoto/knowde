"""系エラー."""


class UnResolvedTermError(Exception):
    """用語解決がまだ."""


class HeadingNotFoundError(Exception):
    """見出しが見つからない."""


class SysNetNotFoundError(Exception):
    """ネットワークに含まれないノード."""

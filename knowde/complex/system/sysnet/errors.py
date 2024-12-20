"""系エラー."""


class UnResolvedTermError(Exception):
    """用語解決がまだ."""


class SysNetNotFoundError(Exception):
    """ネットワークに含まれないノード."""


class AlreadyAddedError(Exception):
    """なぜか既に追加済み."""


class UnaddedYetError(Exception):
    """追加済みのはずなのにまだ追加されていない."""

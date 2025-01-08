"""系エラー."""


class InterpreterError(Exception):
    """構文木解析用."""


class UnResolvedTermError(InterpreterError):
    """用語解決がまだ."""


class SysNetNotFoundError(InterpreterError):
    """ネットワークに含まれないノード."""


class AlreadyAddedError(InterpreterError):
    """なぜか既に追加済み."""


class QuotermNotFoundError(InterpreterError):
    """引用用語が存在しない."""


class DefSentenceConflictError(InterpreterError):
    """定義の文が既出."""

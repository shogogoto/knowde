"""系エラー."""


from typing import NoReturn

from knowde.primitive.__core__.dupchk import DuplicationChecker


class InterpreterError(Exception):
    """構文木解析用."""


class SysNetNotFoundError(InterpreterError):
    """ネットワークに含まれないノード."""


class QuotermNotFoundError(InterpreterError):
    """引用用語が存在しない."""


class DefSentenceConflictError(InterpreterError):
    """定義の文が既出."""


class TermResolveError(InterpreterError):
    """用語解決でのエラー."""


class SentenceConflictError(InterpreterError):
    """1文が重複追加."""


def sentence_dup_checker() -> DuplicationChecker:
    """For dup checker."""

    def _err(s: str) -> NoReturn:
        msg = f"'{s}'は重複しています"
        raise SentenceConflictError(msg)

    return DuplicationChecker(err_fn=_err)

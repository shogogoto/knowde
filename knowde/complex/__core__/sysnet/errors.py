"""系エラー."""
from typing import NoReturn

from knowde.primitive.__core__.dupchk import DuplicationChecker


class UnResolvedTermError(Exception):
    """用語解決がまだ."""


class SysNetNotFoundError(Exception):
    """ネットワークに含まれないノード."""


class AlreadyAddedError(Exception):
    """なぜか既に追加済み."""


class QuotermNotFoundError(Exception):
    """引用用語が存在しない."""


class DefSentenceConflictError(Exception):
    """定義の文が既出."""


class SentenceConflictError(Exception):
    """1文が重複追加."""


def sentence_dup_checker() -> DuplicationChecker:
    """For dup checker."""

    def _err(s: str) -> NoReturn:
        msg = f"'{s}'は重複しています"
        raise SentenceConflictError(msg)

    return DuplicationChecker(err_fn=_err)

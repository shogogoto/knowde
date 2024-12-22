"""系エラー."""
from typing import NoReturn

from knowde.core.dupchk import DuplicationChecker


class UnResolvedTermError(Exception):
    """用語解決がまだ."""


class SysNetNotFoundError(Exception):
    """ネットワークに含まれないノード."""


class AlreadyAddedError(Exception):
    """なぜか既に追加済み."""


class UnaddedYetError(Exception):
    """追加済みのはずなのにまだ追加されていない."""


class SentenceConflictError(Exception):
    """1文が重複追加."""


def sentence_dup_checker() -> DuplicationChecker:
    """For dup checker."""

    def _err(s: str) -> NoReturn:
        msg = f"'{s}は重複しています'"
        raise SentenceConflictError(msg)

    return DuplicationChecker(err_fn=_err)

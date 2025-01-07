"""errors."""
from typing import NoReturn

from knowde.complex.__core__.sysnet.sysnode import SysArg
from knowde.primitive.__core__.dupchk import DuplicationChecker


class LeafExtractError(Exception):
    """ASTリーフ抽出エラー."""


class SentenceConflictError(LeafExtractError):
    """1文が重複追加."""


def raise_extract_error(n: SysArg) -> NoReturn:
    """leaves抽出エラー."""
    msg = f"{type(n)}: {n} is not allowed."
    raise LeafExtractError(msg)


def sentence_dup_checker() -> DuplicationChecker:
    """For dup checker."""

    def _err(s: str) -> NoReturn:
        msg = f"'{s}'は重複しています"
        raise SentenceConflictError(msg)

    return DuplicationChecker(err_fn=_err)


# class SysArgDupChecker(BaseModel):
#     """SysNetへの重複追加チェック."""

#     _term_chk: DuplicationChecker = PrivateAttr(default_factory=term_dup_checker)
#     _s_chk: DuplicationChecker = PrivateAttr(default_factory=sentence_dup_checker)

#     def __call__(self, n: SysArg) -> None:
#         """チェック."""
#         match n:
#             case Term():
#                 self._term_chk(n)
#             case Def():
#                 self._term_chk(n.term)
#                 self._s_chk(n.sentence)
#             case str():
#                 self._s_chk(n)
#             case Duplicable():
#                 pass
#             case _:
#                 msg = f"{type(n)} must be Term or str or Def Type."
#                 raise TypeError(msg, n)

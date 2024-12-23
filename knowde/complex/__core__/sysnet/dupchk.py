"""重複チェック for SysNet."""
from pydantic import BaseModel, PrivateAttr

from knowde.complex.__core__.sysnet.errors import sentence_dup_checker
from knowde.complex.__core__.sysnet.sysnode import Def, SysArg
from knowde.primitive.__core__.dupchk import DuplicationChecker
from knowde.primitive.term import Term, term_dup_checker


class SysArgDupChecker(BaseModel):
    """SysNetへの重複追加チェック."""

    _term_chk: DuplicationChecker = PrivateAttr(default_factory=term_dup_checker)
    _s_chk: DuplicationChecker = PrivateAttr(default_factory=sentence_dup_checker)

    def __call__(self, n: SysArg) -> None:
        """チェック."""
        match n:
            case Term():
                self._term_chk(n)
            case Def():
                self._term_chk(n.term)
                self._s_chk(n.sentence)
            case str():
                self._s_chk(n)
            case _:
                raise TypeError

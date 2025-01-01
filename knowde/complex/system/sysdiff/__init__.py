"""系の差分."""
from __future__ import annotations

from itertools import product

import Levenshtein
from pydantic import BaseModel

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.primitive.term import Term

# class TermDifference


class TermDiff(BaseModel, frozen=True):
    """SysNet間の用語差分."""

    added: set[Term]
    removed: set[Term]

    def __str__(self) -> str:  # noqa: D105
        return f"-{self.removed}\n+{self.added}"

    def n(self) -> tuple[int, int]:  # noqa: D102
        return len(self.added), len(self.removed)


def termdiff(old: SysNet, new: SysNet) -> TermDiff:
    """sn1からsn2への変化."""
    t1 = set(old.terms)
    t2 = set(new.terms)
    added = t2 - t1
    removed = t1 - t2
    return TermDiff(added=added, removed=removed)


class IdentificationError(Exception):
    """同定失敗."""


def identify_sentence(
    old: SysNet,
    new: SysNet,
    threshold_ratio: float = 0.6,
) -> dict[str, str]:
    """変更前後の文の同定."""
    o = set(old.sentences)
    n = set(new.sentences)
    added = n - o
    removed = o - n
    d = {}
    for s_old, s_new in product(removed, added):
        r = Levenshtein.ratio(s_old, s_new)
        if r > threshold_ratio:
            if s_old in d:
                msg = (
                    f"{s_old}と重複して同定されました"
                    f"しきい値{threshold_ratio}を上げてみてください"
                )
                raise IdentificationError(msg, d[s_old], s_new)
            d[s_old] = s_new
    return d


def identify_term(
    old: SysNet,
    new: SysNet,
    threshold_ratio: float = 0.6,
) -> dict[Term, Term]:
    """変更前と変更後を同定."""
    diff = termdiff(old, new)
    d = {}
    s_ident = identify_sentence(old, new, threshold_ratio)
    for t_old, t_new in product(diff.removed, diff.added):
        d1 = old.get(t_old)
        d2 = new.get(t_new)
        # 同じ文に対する異なるtermは同じと同定
        if isinstance(d1, Def) and isinstance(d2, Def):
            if d1.sentence == d2.sentence:
                d[t_old] = t_new
                continue
            if d1.sentence in s_ident:
                pass
    return d

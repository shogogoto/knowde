"""ネットワーク2 node0 系の差分."""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from itertools import product
from typing import TYPE_CHECKING, Self, TypeVar

import Levenshtein
from pydantic import BaseModel

from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.shared.nxutil.edge_type import EdgeType

if TYPE_CHECKING:
    from knowde.feature.parsing.primitive.term import Term
    from knowde.feature.parsing.sysnet import SysNet

# class TermDifference
# diff
# 3種類 term, sentence, edge

T = TypeVar("T")


class SysNodeDiff[T](BaseModel, frozen=True):
    """SysNet間の用語差分."""

    added: set[T]
    removed: set[T]

    def __str__(self) -> str:  # noqa: D105
        return f"-{self.removed}\n+{self.added}"

    def n(self) -> tuple[int, int]:  # noqa: D102
        return len(self.added), len(self.removed)

    @classmethod
    def terms(cls, old: SysNet, new: SysNet) -> Self:  # noqa: D102
        t1 = set(old.terms)
        t2 = set(new.terms)
        return cls(added=t2 - t1, removed=t1 - t2)

    @classmethod
    def sentences(cls, old: SysNet, new: SysNet) -> Self:  # noqa: D102
        s1 = set(old.sentences)
        s2 = set(new.sentences)
        return cls(added=s2 - s1, removed=s1 - s2)

    def product(self) -> Iterable[tuple[T, T]]:  # noqa: D102
        return product(self.removed, self.added)


class IdentificationError(Exception):
    """同定失敗."""


def identify_sentence(
    old: SysNet,
    new: SysNet,
    threshold_ratio: float = 0.6,
) -> dict[str, str]:
    """変更前後の文の同定."""
    diff = SysNodeDiff.sentences(old, new)
    d = {}
    for s_old, s_new in diff.product():
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
    """変更前後のtermを同定."""
    diff = SysNodeDiff.terms(old, new)
    d = {}
    for t_old, t_new in diff.product():
        d1 = old.get(t_old)
        d2 = new.get(t_new)
        # 同じ文に対する異なるtermは同じと同定
        if isinstance(d1, Def) and isinstance(d2, Def) and d1.sentence == d2.sentence:
            d[t_old] = t_new
    s_ident = identify_sentence(old, new, threshold_ratio)
    for t_old in diff.removed:
        d1 = old.get(t_old)
        if isinstance(d1, Def) and d1.sentence in s_ident:
            s_new = s_ident[d1.sentence]
            d2 = new.get(s_new)
            if isinstance(d2, Def):
                d[t_old] = d2.term
    return d


type TypedEdge = tuple[Hashable, EdgeType, Hashable]


def edges2tuples(sn: SysNet) -> set[TypedEdge]:
    """edgeをsetに変換."""
    edges = set()
    for s in sn.sentences:
        e = {(u, attr["type"], v) for u, v, attr in sn.g.out_edges(s, data=True)}
        edges = edges.union(e)
    return edges


def edgestr(te: TypedEdge) -> str:
    """To string."""
    u, t, v = te
    return f"'{u}'-[{t.name}]->'{v}'"


class EdgeDiff(BaseModel, frozen=True):
    """関係変更."""

    added: set[TypedEdge]
    removed: set[TypedEdge]

    def __str__(self) -> str:  # noqa: D105
        lines = []
        lines.extend(f"- {edgestr(r)}" for r in self.removed)
        lines.extend(f"+ {edgestr(r)}" for r in self.added)
        return "\n".join(lines)


def edgediff(old: SysNet, new: SysNet) -> EdgeDiff:
    """関係の差分."""
    old_edges = edges2tuples(old)
    new_edges = edges2tuples(new)
    added = new_edges - old_edges
    removed = old_edges - new_edges
    return EdgeDiff(added=added, removed=removed)

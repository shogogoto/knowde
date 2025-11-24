"""差分更新.

DB機能なしのdomain
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from itertools import product
from typing import TYPE_CHECKING

import Levenshtein

from knowde.feature.entry.resource.repo.diff_update.errors import IdentificationError
from knowde.feature.entry.resource.repo.save import EdgeRel
from knowde.feature.parsing.sysnet.sysnode import KNode

if TYPE_CHECKING:
    from knowde.feature.parsing.primitive.term import Term
    from knowde.feature.parsing.sysnet import SysNet

type UpdateGetter[T] = Callable[[Iterable[T], Iterable[T]], dict[T, T]]


def identify_updatediff_txt(
    old: Iterable[str],
    new: Iterable[str],
    threshold_ratio: float = 0.6,
) -> dict[str, str]:
    """2種類の文の集合の更新対を同定."""
    o, n = set(old), set(new)
    removed, added = o - n, n - o
    d = {}
    for txt1, txt2 in product(removed, added):
        r = Levenshtein.ratio(txt1, txt2)
        if r > threshold_ratio:
            if txt1 in d:
                msg = (
                    f"{txt1}と重複して同定されました."
                    f"閾値{threshold_ratio}を上げてみてください"
                )
                raise IdentificationError(msg, d[txt1], txt2)
            d[txt1] = txt2
    return d


def diff2sets[T](old: Iterable[T], new: Iterable[T]) -> tuple[set[T], set[T]]:
    """差分をsetに変換."""
    o, n = set(old), set(new)
    removed, added = o - n, n - o
    return removed, added


def create_updatediff[T](
    old: Iterable[T],
    new: Iterable[T],
    f: UpdateGetter[T],
) -> tuple[set[T], set[T], dict[T, T]]:
    """更新差分の作成."""
    removed, added = diff2sets(old, new)
    updated = f(removed, added)
    removed -= set(updated.keys())
    added -= set(updated.values())
    return removed, added, updated


def identify_updatediff_term(
    old: Iterable[Term],
    new: Iterable[Term],
    threshold_ratio: float = 0.6,
) -> dict[Term, Term]:
    """2種類の用語の集合の更新対を同定."""
    r_txts = {str(t): t for t in old}
    a_txts = {str(t): t for t in new}
    updiff = identify_updatediff_txt(r_txts.keys(), a_txts.keys(), threshold_ratio)
    return {r_txts[k]: a_txts[v] for k, v in updiff.items()}


def sysnet2edges(sn: SysNet) -> set[EdgeRel]:
    """edgeをsetに変換."""
    edges = set()
    for s in sn.sentences:  # 単文の関係だけ見れば良い
        e = {(u, v, attr["type"]) for u, v, attr in sn.g.out_edges(s, data=True)}
        edges = edges.union(e)
    return edges


def edges2nodes(es: Iterable[EdgeRel]) -> set[KNode]:
    """edgeをnodeに変換."""
    s = set()
    for e in es:
        u, v, _ = e
        s.add(u)
        s.add(v)
    return s

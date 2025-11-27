"""差分更新domain."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from itertools import product
from typing import TYPE_CHECKING

import Levenshtein

from knowde.feature.entry.resource.repo.diff_update.errors import IdentificationError
from knowde.feature.entry.resource.repo.save import EdgeRel
from knowde.feature.parsing.sysnet.sysnode import Def, Sentency
from knowde.shared.types import Duplicable

if TYPE_CHECKING:
    from knowde.feature.parsing.primitive.term import Term
    from knowde.feature.parsing.sysnet import SysNet

type UpdateGetter[T] = Callable[[Iterable[T], Iterable[T]], dict[T, T]]


def identify_updatediff_txt(
    old: Iterable[str],
    new: Iterable[str],
    threshold_ratio: float = 0.6,
) -> dict[Sentency, Sentency]:
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
    rm, add = diff2sets(old, new)
    updated = f(rm, add)
    rm -= set(updated.keys())
    add -= set(updated.values())
    return rm, add, updated


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
    for s in [*sn.sentences, sn.root]:  # 単文の関係だけ見れば良い
        e = {(u, v, attr["type"]) for u, v, attr in sn.g.out_edges(s, data=True)}
        edges = edges.union(e)
    return edges


def edges2nodes(es: Iterable[EdgeRel]) -> set[Sentency]:
    """edgeをnodeに変換."""
    s = set()
    for e in es:
        u, v, _ = e
        s.add(u)
        s.add(v)
    return s


def get_switched_def_terms(old: SysNet, upd: SysNet) -> dict[Term, Term]:
    """用語と単文の入れ替えを取得する.

    単文はそのままにしたいので、操作すべきtermsを返す
    """
    old_defs = {old.get(t) for t in old.terms}
    old_defs = {d for d in old_defs if isinstance(d, Def)}  # 型付け
    d = {}
    for old_d in old_defs:
        if old_d.sentence not in upd.g:
            continue
        upd_d = upd.get(old_d.sentence)
        if isinstance(upd_d, Def) and upd_d.term != old_d.term:
            d[old_d.term] = upd_d.term
    return d


def identify_duplicate_updiff(
    old: SysNet,
    upd: SysNet,
) -> dict[Sentency, Sentency]:
    """Dupl <-> strの変更を用語共有で同定."""
    map_ = {}
    # Dupl -> str
    old_d = [
        d
        for d in [old.get(s) for s in old.sentences]
        if isinstance(d, Def) and isinstance(d.sentence, Duplicable)
    ]
    for od in old_d:
        if od.term not in upd.g:
            continue
        d = upd.get(od.term)
        if isinstance(d, Def) and od.sentence != d.sentence:
            map_[od.sentence] = d.sentence

    # str -> Dupl
    upd_d = [
        d
        for d in [upd.get(s) for s in upd.sentences]
        if isinstance(d, Def) and isinstance(d.sentence, Duplicable)
    ]
    for ud in upd_d:
        if ud.term not in old.g:
            continue
        d = old.get(ud.term)
        if isinstance(d, Def) and ud.sentence != d.sentence:
            map_[d.sentence] = ud.sentence
    return map_

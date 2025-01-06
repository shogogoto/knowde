"""用語の参照関係."""
from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, AbstractSet, TypeAlias

from knowde.primitive.term import Term
from knowde.primitive.term.mark.domain import (
    pick_marks,
    replace_markers,
)

if TYPE_CHECKING:
    import networkx as nx


def get_refer_terms(
    targets: AbstractSet[Term],
    referred: frozenset[Term],
) -> frozenset[Term]:
    """referredを参照するmarktermのみを返す."""
    diff = targets - referred
    lookup = get_lookup(referred)
    ret = set()
    for t in diff:
        for n in t.names:
            marks = pick_marks(n)
            if all(m in lookup for m in marks):
                ret.add(t)
    return frozenset(ret)


Lookup: TypeAlias = dict[str, Term]  # mark Term辞書


@cache
def get_lookup(terms: frozenset[Term]) -> Lookup:
    """{name|alias: Term}の辞書を作成."""
    d = {}
    for t in terms:
        for n in t.names:
            marks = pick_marks(n)
            atom = replace_markers(n, *marks)
            d[atom] = t
        if t.alias:
            d[t.alias] = t
    return d


# def next_lookup(old: Lookup, refer: AbstractSet[Term]) -> Lookup:
#     """lookupを参照するtermを結合して返す."""
#     lookup = get_lookup(frozenset(refer))
#     get_refer_terms()


def to_markterm_graph(terms: AbstractSet[Term]) -> tuple[nx.DiGraph, Lookup]:
    """markの依存関係グラフ."""
    atomic = frozenset({t for t in terms if not t.has_mark()})
    _refer = get_refer_terms(terms, atomic)
    _lookup = get_lookup(atomic)

    # print("#" * 80)
    # print(refer)
    # print(lookup)

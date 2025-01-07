"""用語の参照関係."""
from __future__ import annotations

from functools import cache
from typing import AbstractSet, TypeAlias

from knowde.primitive.term import Term
from knowde.primitive.term.errors import MarkUncontainedError
from knowde.primitive.term.mark.domain import (
    pick_marks,
    replace_markers,
)


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


def to_lookup(terms: AbstractSet[Term]) -> Lookup:
    """markの依存関係グラフ."""
    referred = frozenset({t for t in terms if not t.has_mark()})
    lookup = get_lookup(referred)
    diff = terms - referred
    while len(diff) > 0:
        refer = get_refer_terms(terms, referred)
        lookup = lookup | get_lookup(refer)
        referred = referred | refer
        _next = terms - referred
        if _next == diff:  # 同じdiffが残り続ける
            marks = next(iter(_next)).marks
            m = next(m for m in marks if m not in lookup)
            msg = f"'{m}'を解決できませんでした"
            raise MarkUncontainedError(msg, set(_next))
        diff = _next
    # g = reduce(nx.compose, [t.marktree for t in terms])
    return lookup

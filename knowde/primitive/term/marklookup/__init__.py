"""用語の参照関係."""

from __future__ import annotations

from functools import cache

from knowde.primitive.term import Term
from knowde.primitive.term.const import BRACE_MARKER
from knowde.primitive.term.errors import MarkUncontainedError


def get_refer_terms(
    targets: set[Term],
    referred: frozenset[Term],
) -> frozenset[Term]:
    """referredを参照するmarktermのみを返す."""
    diff = targets - referred
    lookup = get_lookup(referred)
    ret = set()
    for t in diff:
        for n in t.names:
            marks = BRACE_MARKER.pick(n)
            if all(m in lookup for m in marks):
                ret.add(t)
    return frozenset(ret)


type Lookup = dict[str, Term]  # mark Term辞書


@cache
def get_lookup(terms: frozenset[Term]) -> Lookup:
    """{name|alias: Term}の辞書を作成."""
    d = {}
    for t in terms:
        for n in t.names:
            marks = BRACE_MARKER.pick(n)
            atom = BRACE_MARKER.replace(n, *marks)
            d[atom] = t
        if t.alias:
            d[t.alias] = t
    return d


def to_lookup(terms: set[Term]) -> Lookup:
    """markの依存関係グラフ."""
    referred = frozenset({t for t in terms if not t.has_mark()})
    lookup = get_lookup(referred)
    diff = terms - referred
    while len(diff) > 0:
        refer = get_refer_terms(terms, referred)
        lookup |= get_lookup(refer)
        referred |= refer
        next_ = terms - referred
        if next_ == diff:  # 同じdiffが残り続ける
            marks = next(iter(next_)).marks
            m = next(m for m in marks if m not in lookup)
            msg = f"'{m}'を解決できませんでした"
            raise MarkUncontainedError(msg, set(next_))
        diff = next_
    # g = reduce(nx.compose, [t.marktree for t in terms])
    return lookup

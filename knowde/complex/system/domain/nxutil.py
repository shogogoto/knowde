"""networkx関連."""
from typing import Any, Callable, Hashable, Iterable, TypeAlias

import networkx as nx

FRecursive: TypeAlias = Callable[[nx.DiGraph, Hashable], Iterable[Hashable]]


def to_nested(
    g: nx.DiGraph,
    start: Hashable,
    f: FRecursive,
) -> dict:
    """有向グラフから入れ子の辞書を作成."""

    def _f(n: Hashable) -> dict:
        children = list(f(g, n))
        if not children:
            return {}
        return {child: _f(child) for child in children}

    return _f(start)


def succ_nested(g: nx.DiGraph, start: Hashable) -> dict:
    """子孫の入れ子の辞書を取得する関数."""
    return to_nested(g, start, lambda g, n: g.successors(n))


def succ_attr(attr_name: str, value: Any) -> FRecursive:  # noqa: ANN401
    """次を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterable[Hashable]:
        for succ in g.successors(start):
            if g.edges[start, succ].get(attr_name) == value:
                _f(g, succ)
                yield succ

    return _f

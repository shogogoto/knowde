"""networkx関連."""
from __future__ import annotations

from pprint import pp
from typing import Any, Callable, Hashable, Iterable, TypeAlias

import networkx as nx

FChildren: TypeAlias = Callable[[nx.DiGraph, Hashable], Iterable[Hashable]]


def to_nested(
    g: nx.DiGraph,
    start: Hashable,
    f: FChildren,
) -> dict:
    """有向グラフから入れ子の辞書を作成."""

    def _f(n: Hashable) -> dict:
        children = list(f(g, n))
        if not children:
            return {}
        return {child: _f(child) for child in children}

    return _f(start)


def to_nodes(
    g: nx.DiGraph,
    start: Hashable,
    f: FChildren,
) -> set[Hashable]:
    """有向グラフを辿ってノードを取得."""
    s = set()

    def _f(n: Hashable) -> None:
        children = list(f(g, n))
        s.add(n)
        s.union([_f(child) for child in children])

    _f(start)
    return s


def succ_attr(attr_name: str, value: Any) -> FChildren:  # noqa: ANN401
    """次を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterable[Hashable]:
        for succ in g.successors(start):
            if g.edges[start, succ].get(attr_name) == value:
                _f(g, succ)
                yield succ

    return _f


def nxprint(g: nx.DiGraph) -> None:
    """確認用."""
    print("")  # noqa: T201
    nx.write_network_text(g)
    pp(nx.to_dict_of_dicts(g))

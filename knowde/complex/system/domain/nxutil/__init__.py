"""networkx関連."""
from __future__ import annotations

from pprint import pp
from typing import Any, Callable, Hashable, Iterator, TypeAlias

import networkx as nx

Accessor: TypeAlias = Callable[[nx.DiGraph, Hashable], Iterator[Hashable]]


def to_nested(
    g: nx.DiGraph,
    start: Hashable,
    f: Accessor,
) -> dict:
    """有向グラフから入れ子の辞書を作成."""

    def _f(n: Hashable) -> dict:
        nlist = list(f(g, n))
        if not nlist:
            return {}
        return {anode: _f(anode) for anode in nlist}

    return _f(start)


def to_nodes(
    g: nx.DiGraph,
    start: Hashable,
    f: Accessor,
) -> set[Hashable]:
    """有向グラフを辿ってノードを取得."""
    s = set()

    def _f(n: Hashable) -> None:
        nlist = list(f(g, n))
        s.add(n)
        s.union([_f(anode) for anode in nlist])

    _f(start)
    return s


def succ_attr(attr_name: str, value: Any) -> Accessor:  # noqa: ANN401
    """次を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterator[Hashable]:
        for succ in g.successors(start):
            if g.edges[start, succ].get(attr_name) == value:
                _f(g, succ)
                yield succ

    return _f


def pred_attr(attr_name: str, value: Any) -> Accessor:  # noqa: ANN401
    """前を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterator[Hashable]:
        for pred in g.predecessors(start):
            if g.edges[pred, start].get(attr_name) == value:
                _f(g, pred)
                yield pred

    return _f


def nxprint(g: nx.DiGraph) -> None:
    """確認用."""
    print("")  # noqa: T201
    nx.write_network_text(g)
    pp(nx.to_dict_of_dicts(g))

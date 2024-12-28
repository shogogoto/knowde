"""networkx関連."""
from __future__ import annotations

from functools import cache
from pprint import pp
from typing import Any, Hashable

import networkx as nx

from .edge_type import Direction, EdgeType  # noqa: F401
from .types import Accessor, Edges


def nxprint(g: nx.DiGraph, detail: bool = False) -> None:  # noqa: FBT001 FBT002
    """確認用."""
    print("")  # noqa: T201
    nx.write_network_text(g)
    if detail:
        pp(nx.to_dict_of_dicts(g))


@cache
def to_nested(g: nx.DiGraph, start: Hashable, f: Accessor) -> dict:
    """有向グラフから入れ子の辞書を作成."""

    def _f(n: Hashable) -> dict:
        nlist = list(f(g, n))
        if not nlist:
            return {}
        return {anode: _f(anode) for anode in nlist}

    return _f(start)


def to_nodes(g: nx.DiGraph, start: Hashable, f: Accessor) -> list[Hashable]:
    """有向グラフを辿ってノードを取得."""
    s = []

    def _f(n: Hashable) -> None:
        nlist = list(f(g, n))
        s.append(n)
        s.extend([_f(anode) for anode in nlist])

    _f(start)
    return s


def filter_edge_attr(g: nx.DiGraph, name: str, value: Any) -> nx.DiGraph:  # noqa: ANN401
    """ある属性のエッジのみを抽出する関数を返す."""

    def _f(u: Hashable, v: Hashable) -> bool:
        return g[u][v][name] == value

    return nx.subgraph_view(g, filter_edge=_f)


def _to_paths(g: nx.DiGraph, pairs: Edges) -> list[list[Hashable]]:
    paths = []
    for u, v in pairs:
        try:
            p = list(nx.shortest_path(g, u, v))
            paths.append(p)
        except nx.NetworkXNoPath:  # noqa: PERF203
            continue
    return paths


def leaf_paths(g: nx.DiGraph, tgt: Hashable, t: Any) -> list[list[Hashable]]:  # noqa: ANN401
    """入力ノードから特定の関係を遡って依存先がないノードまでのパスを返す."""
    sub = filter_edge_attr(g, "type", t)
    edges = [
        (tgt, n) for n in sub.nodes if sub.out_degree(n) == 0 and sub.degree(n) != 0
    ]
    return _to_paths(sub, edges)


def axiom_paths(g: nx.DiGraph, tgt: Hashable, t: Any) -> list[list[Hashable]]:  # noqa: ANN401
    """入力ノードから特定の関係を遡って依存元がないノードまでのパスを返す."""
    sub = filter_edge_attr(g, "type", t)
    pairs = [
        (n, tgt) for n in sub.nodes if sub.in_degree(n) == 0 and sub.degree(n) != 0
    ]
    return _to_paths(sub, pairs)


def replace_node(g: nx.DiGraph, old: Hashable, new: Hashable) -> None:
    """エッジを保ってノードを置換."""
    g.add_node(new)

    for pred, _, data in g.in_edges(old, data=True):
        g.add_edge(pred, new, **data)
    for _, succ, data in g.out_edges(old, data=True):
        g.add_edge(new, succ, **data)
    g.remove_node(old)

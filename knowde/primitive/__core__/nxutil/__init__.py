"""networkx関連."""

from __future__ import annotations

from collections.abc import Hashable
from functools import cache
from pprint import pp
from typing import TYPE_CHECKING, Any

import networkx as nx

if TYPE_CHECKING:
    from .edge_type import EdgeType
    from .types import Accessor, Edges


def nxprint(g: nx.DiGraph, detail: bool = False) -> None:  # noqa: FBT001 FBT002
    """確認用."""
    print()  # noqa: T201
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


@cache
def to_nodes(g: nx.DiGraph, start: Hashable, f: Accessor) -> list[Hashable]:
    """有向グラフを辿ってノードを取得."""
    s = []

    def _f(n: Hashable) -> None:
        nlist = list(f(g, n))
        s.append(n)
        s.extend([_f(anode) for anode in nlist])

    _f(start)
    return s


@cache
def filter_edge_attr(g: nx.DiGraph, name: str, *values: Any) -> nx.DiGraph:
    """ある属性のエッジのみを抽出する関数を返す."""

    def _f(u: Hashable, v: Hashable, attr: dict) -> bool:
        return g[u][v][attr][name] in values

    return nx.subgraph_view(g, filter_edge=_f)


def _to_paths(g: nx.DiGraph, pairs: Edges) -> list[list[Hashable]]:
    paths = []
    for u, v in pairs:
        try:
            p = list(nx.shortest_path(g, u, v))
            paths.append(p)
        except nx.NetworkXNoPath:
            continue
    return paths


@cache
def to_leaves(g: nx.DiGraph, *ts: Any) -> list[Hashable]:
    """最先端を取得."""
    sub = filter_edge_attr(g, "type", *ts)
    return [n for n in sub.nodes if sub.out_degree(n) == 0 and sub.in_degree(n) != 0]


@cache
def to_roots(g: nx.DiGraph, *ts: Any) -> list[Hashable]:
    """根を取得."""
    sub = filter_edge_attr(g, "type", *ts)
    return [n for n in sub.nodes if sub.in_degree(n) == 0 and sub.out_degree(n) != 0]


def leaf_paths(g: nx.DiGraph, tgt: Hashable, t: Any) -> list[list[Hashable]]:
    """入力ノードから特定の関係を遡って依存先がないノードまでのパスを返す."""
    sub = filter_edge_attr(g, "type", t)
    pairs = [(tgt, lv) for lv in to_leaves(g, t)]
    return _to_paths(sub, pairs)


def root_paths(g: nx.DiGraph, tgt: Hashable, t: Any) -> list[list[Hashable]]:
    """入力ノードから特定の関係を遡って依存元がないノードまでのパスを返す."""
    sub = filter_edge_attr(g, "type", t)
    pairs = [(n, tgt) for n in to_roots(g, t)]
    return _to_paths(sub, pairs)


def copy_old_edges(
    g: nx.DiGraph,
    old: Hashable,
    new: Hashable,
    *ignore: EdgeType,
) -> None:
    """oldエッジをnew nodeにコピー."""
    g.add_node(new)

    for pred, _, data in g.in_edges(old, data=True):
        if data["type"] in ignore:
            continue
        g.add_edge(pred, new, **data)
    for _, succ, data in g.out_edges(old, data=True):
        if data["type"] in ignore:
            continue
        g.add_edge(new, succ, **data)


def get_roots(g: nx.MultiDiGraph, *types: Any) -> list[Hashable]:
    """出発点を取得."""

    def _f(u: Hashable, v: Hashable, attr: dict) -> bool:
        return g[u][v][attr]["type"] in types

    sub: nx.MultiDiGraph = nx.subgraph_view(g, filter_edge=_f)

    return [n for n in sub.nodes if sub.in_degree(n) == 0 and sub.degree(n) != 0]

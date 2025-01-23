"""1network 1nodeを引数にする関数."""
from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Callable, Final, Iterable, TypeAlias

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg, SysNode
from knowde.primitive.__core__.nxutil import (
    filter_edge_attr,
    to_axioms,
    to_nodes,
)
from knowde.primitive.__core__.nxutil.edge_type import EdgeType, etype_subgraph

if TYPE_CHECKING:
    import networkx as nx

Nw1N1Fn: TypeAlias = Callable[[SysNet, SysNode], list[SysNode]]


def get_detail(sn: SysNet, n: SysNode) -> list[SysNode]:
    """詳細な記述."""
    vals = []
    sub = etype_subgraph(sn.g, EdgeType.SIBLING, EdgeType.BELOW)
    for below_s in EdgeType.BELOW.succ(sub, n):
        sibs = to_nodes(sub, below_s, EdgeType.SIBLING.succ)
        vals.extend([s for s in sibs if s])  # None排除
    return vals


class ParentLookupError(Exception):
    """親テーブルを作る時に変なことが起きた."""


@cache
def parent_lookup(g: nx.DiGraph) -> dict:
    """親の辞書."""
    g = filter_edge_attr(g, "type", EdgeType.BELOW, EdgeType.SIBLING)
    parents = to_axioms(g, EdgeType.BELOW)
    lookup = {}
    for p in parents:
        first_sibs = EdgeType.BELOW.succ(g, p)
        for s in first_sibs:
            lookup[s] = p
            for _s in [e for e in to_nodes(g, s, EdgeType.SIBLING.succ) if e]:
                lookup[_s] = p
    return lookup


def get_parent_or_none(sn: SysNet, n: SysNode) -> SysNode | None:
    """兄弟を辿ったらBELOW.predが存在するか."""
    lookup = parent_lookup(sn.sentence_graph)
    return lookup.get(n)


def get_refer(sn: SysNet, n: SysNode) -> list[SysNode]:
    """引用・利用する側."""
    vals = EdgeType.RESOLVED.pred(sn.g, n)
    return list(vals)


def get_referred(sn: SysNet, n: SysNode) -> list[SysNode]:
    """引用される依存元."""
    vals = EdgeType.RESOLVED.succ(sn.g, n)
    return list(vals)


def get_premise(sn: SysNet, n: SysNode) -> list[SysNode]:
    """前提."""
    vals = EdgeType.TO.pred(sn.g, n)
    return list(vals)


def get_conclusion(sn: SysNet, n: SysNode) -> list[SysNode]:
    """帰結."""
    vals = EdgeType.TO.succ(sn.g, n)
    return list(vals)


def get_example(sn: SysNet, n: SysNode) -> list[SysNode]:
    """具体."""
    vals = EdgeType.EXAMPLE.succ(sn.g, n)
    return list(vals)


def get_general(sn: SysNet, n: SysNode) -> list[SysNode]:
    """抽象."""
    vals = EdgeType.EXAMPLE.pred(sn.g, n)
    return list(vals)


def recursively_nw1n1(fn: Nw1N1Fn, count: int) -> Nw1N1Fn:
    """再帰的取得."""
    if count < 1:
        msg = "recursive count must be greater than 0"
        raise ValueError(msg)

    def _f(sn: SysNet, ns: Iterable, i: int) -> Iterable:
        """再帰."""
        if i == 0:
            return ns
        return [e if isinstance(e, list) else [e, _f(sn, fn(sn, e), i - 1)] for e in ns]

    def _g(sn: SysNet, n: SysNode) -> list:
        ret = fn(sn, n)
        return list(_f(sn, ret, count - 1))

    return _g


#######################################################

# 依存性関連エッジ
DEP_EDGE_TYPES: Final = [
    EdgeType.TO,
    EdgeType.EXAMPLE,
    EdgeType.SIMILAR,
    EdgeType.ANTI,
    EdgeType.RESOLVED,
]


@cache
def has_dependency(sn: SysNet, n: SysArg) -> bool:
    """意味的に重要なエッジを持つ."""
    _in = sn.g.in_edges(n, data=True)
    for _u, _, attr in _in:
        if attr["type"] in DEP_EDGE_TYPES:
            return True

    _out = sn.g.out_edges(n, data=True)
    return any(attr["type"] in DEP_EDGE_TYPES for _, _v, attr in _out)

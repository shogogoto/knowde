"""1network 1nodeを引数にする関数."""
from __future__ import annotations

from functools import cache
from typing import Callable, Final, Iterable, TypeAlias

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg, SysNode
from knowde.primitive.__core__.nxutil import axiom_paths, to_nodes
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.heading import get_headings

Nw1N1Fn: TypeAlias = Callable[[SysNet, SysNode], list[SysArg]]


def get_detail(sn: SysNet, n: SysArg) -> list[SysArg]:
    """詳細な記述."""
    vals = []
    for below_s in EdgeType.BELOW.succ(sn.g, n):
        sibs = to_nodes(sn.g, below_s, EdgeType.SIBLING.succ)
        vals.extend([sn.get(s) for s in sibs if s])  # None排除
    return vals


def get_parent_or_none(sn: SysNet, n: SysNode) -> SysNode | None:
    """兄弟を辿ったらBELOW.predが存在するか."""
    axioms = axiom_paths(sn.g, n, EdgeType.SIBLING)
    if len(axioms) == 0:
        return None
    axiom = axioms[0][0]
    parent = list(EdgeType.BELOW.pred(sn.g, axiom))
    if len(parent) == 0:
        return None
    if parent[0] in get_headings(sn.g, sn.root):
        return None
    return parent[0]


def get_refer(sn: SysNet, n: SysNode) -> list[SysArg]:
    """引用・利用する側."""
    vals = list(EdgeType.RESOLVED.pred(sn.g, n))
    return list(map(sn.get, vals))


def get_referred(sn: SysNet, n: SysNode) -> list[SysArg]:
    """引用される依存元."""
    vals = list(EdgeType.RESOLVED.succ(sn.g, n))
    return list(map(sn.get, vals))


def get_premise(sn: SysNet, n: SysNode) -> list[SysArg]:
    """前提."""
    vals = list(EdgeType.TO.pred(sn.g, n))
    return list(map(sn.get, vals))


def get_conclusion(sn: SysNet, n: SysNode) -> list[SysArg]:
    """帰結."""
    vals = list(EdgeType.TO.succ(sn.g, n))
    return list(map(sn.get, vals))


def recursively_nw1n1(fn: Nw1N1Fn, count: int) -> Nw1N1Fn:
    """再帰的取得."""
    if count < 1:
        raise ValueError

    def _f(sn: SysNet, ns: Iterable[SysNode], i: int) -> Iterable:
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
    _out = sn.g.out_edges(n, data=True)

    for _u, _, attr in _in:
        if attr["type"] in DEP_EDGE_TYPES:
            return True

    return any(attr["type"] in DEP_EDGE_TYPES for _, _v, attr in _out)

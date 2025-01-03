"""1network 1nodeを引数にする関数."""
from __future__ import annotations

from typing import Hashable

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg, SysNode
from knowde.primitive.__core__.nxutil import axiom_paths, to_nodes
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.heading import get_headings


def get_details(sn: SysNet, n: Hashable) -> list[SysNode]:
    """詳細な記述."""
    vals = []
    for below_s in EdgeType.BELOW.succ(sn.g, n):
        sibs = to_nodes(sn.g, below_s, EdgeType.SIBLING.succ)
        vals.append([sn.get(s) for s in sibs if s])  # None排除
    return vals


def get_parent_or_none(sn: SysNet, n: SysArg) -> SysNode | None:
    """兄弟を辿ったらBELOW.predが存在するか."""
    EdgeType.SIBLING.pred(sn.g, n)
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

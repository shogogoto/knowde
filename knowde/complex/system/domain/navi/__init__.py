"""ナビ 任意sysnodeの位置を把握する羅針盤."""
from __future__ import annotations

import networkx as nx

from knowde.complex.system.domain.sysnet import SystemNetwork
from knowde.complex.system.domain.sysnet.sysnode import SysNodeType

from .errors import HeadingNotFoundError


def heading_path(sn: SystemNetwork, n: SysNodeType) -> list[SysNodeType]:
    """直近の見出しパス."""
    paths = list(nx.shortest_simple_paths(sn.g, sn.root, n))
    if len(paths) == 0:
        raise HeadingNotFoundError
    p = paths[0]
    return [e for e in p if e in sn.headings]


def axiom_paths(sy: SystemNetwork, n: SysNodeType) -> None:
    pass

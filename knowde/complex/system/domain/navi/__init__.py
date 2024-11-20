"""ナビ sysnodeの位置を把握する羅針盤.

sysnetのユーザー
"""
from __future__ import annotations

from typing import Hashable

import networkx as nx

from knowde.complex.system.domain.sysnet import SystemNetwork


class HeadingNotFoundError(Exception):
    """見出しが見つからない."""


def heading_path(sn: SystemNetwork, n: Hashable) -> list[Hashable]:
    """直近の見出しパス."""
    paths = list(nx.shortest_simple_paths(sn.g, sn.root, n))
    if len(paths) == 0:
        raise HeadingNotFoundError
    p = paths[0]
    return [e for e in p if e in sn.headings]

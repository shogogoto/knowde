"""見出し操作."""
from __future__ import annotations

from typing import Hashable

import networkx as nx

from knowde.primitive.__core__.nxutil import EdgeType, to_nodes


class HeadingNotFoundError(Exception):
    """見出しが見つからない."""


def get_headings(g: nx.DiGraph, root: Hashable) -> set[str]:
    """見出しセット."""
    ns = to_nodes(g, root, EdgeType.HEAD.succ)
    return {str(n) for n in ns if n}


def get_heading_path(g: nx.DiGraph, root: Hashable, n: Hashable) -> list[Hashable]:
    """直近の見出しパス."""
    paths = list(nx.all_simple_paths(g.to_undirected(), root, n))
    if len(paths) == 0:
        raise HeadingNotFoundError
    minp = paths[0]
    for p in paths:
        if len(minp) > len(p):
            minp = p
    return [e for e in minp if e in get_headings(g, root)]

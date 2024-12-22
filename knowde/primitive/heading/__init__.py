"""見出し操作."""
from __future__ import annotations

from typing import Hashable

import networkx as nx

from knowde.primitive.__core__.nxutil import EdgeType, succ_attr, to_nodes


class HeadingNotFoundError(Exception):
    """見出しが見つからない."""


def get_headings(g: nx.DiGraph, root: Hashable) -> set[str]:
    """見出しセット."""
    ns = to_nodes(g, root, succ_attr("type", EdgeType.HEAD))
    return {str(n) for n in ns}


def get_heading_path(g: nx.DiGraph, root: Hashable, n: Hashable) -> list[Hashable]:
    """直近の見出しパス."""
    paths = list(nx.shortest_simple_paths(g.to_undirected(), root, n))
    if len(paths) == 0:
        raise HeadingNotFoundError
    p = paths[0]
    return [e for e in p if e in get_headings(g, root)]

"""見出し操作."""

from __future__ import annotations

from collections.abc import Hashable
from functools import cache
from typing import Final

import networkx as nx
from lark import Token


class HeadingNotFoundError(Exception):
    """見出しが見つからない."""


HEADING: Final = ["H1", "H2", "H3", "H4", "H5", "H6"]


@cache
def get_headings(g: nx.DiGraph, root: Hashable) -> set[str]:
    """見出しセット."""
    return {str(n) for n in g.nodes if isinstance(n, Token) and n.type in HEADING}


@cache
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

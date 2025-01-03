"""RESOLVED関係の構築."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.term import Term

if TYPE_CHECKING:
    import networkx as nx


def add_resolve_edge(g: nx.DiGraph, start: str, termd: dict[Term, dict]) -> None:
    """(start)-[RESOLVE]->(marked sentence)."""
    for k, v in termd.items():
        ls = list(EdgeType.DEF.succ(g, k))  # DEFを使うのなら実質SysNetに依存
        if len(ls) == 0:
            continue
        s = ls[0]  # 文
        EdgeType.RESOLVED.add_edge(g, start, s)  # 文 -> 文
        if any(v):  # 空でない
            add_resolve_edge(g, s, v)

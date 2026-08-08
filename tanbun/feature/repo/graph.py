"""neo4jとnetworkx間の変換."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx
from neo4j.graph import Path as NeoPath

from tanbun.feature.domain.graph.edge_type import EdgeType


def neo4jpath2nx(paths: Iterable[NeoPath]) -> nx.MultiDiGraph:
    """neo4jをnxに変換."""
    g = nx.MultiDiGraph()
    for p in paths:
        for rel in p.relationships:
            s = rel.start_node.get("uid") if rel.start_node else None
            e = rel.end_node.get("uid") if rel.end_node else None
            t = EdgeType[rel.type]
            g.add_edge(s, e, type=t)
    return g

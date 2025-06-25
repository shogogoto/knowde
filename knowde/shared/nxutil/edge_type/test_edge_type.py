"""edge type test."""

import networkx as nx
from pytest_unordered import unordered

from knowde.shared.nxutil.edge_type import EdgeType


def test_subgraph() -> None:
    """サブグラフの取得."""
    g = nx.MultiDiGraph()

    t = EdgeType.TO
    t.add_edge(g, "a", "a0")
    t.add_edge(g, "a", "a1")
    EdgeType.ANTI.add_edge(g, "a", "x")
    t.add_edge(g, "a1", "a11")
    sub = t.subgraph(g)
    assert list(sub.nodes) == unordered(["a", "a0", "a1", "a11"])

"""test."""


from pathlib import Path

import networkx as nx

from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.__core__.nxutil.io import nxread, nxwrite


def test_io(tmp_path: Path) -> None:
    """ファイルIO."""
    d = tmp_path / "nxio"
    d.mkdir()
    p = d / "io.json"
    g1 = nx.generators.balanced_tree(5, 2, nx.MultiDiGraph)
    EdgeType.BELOW.add_edge(g1, "pre", "suc")  # EdgeTypeのjson 変換
    nxwrite(g1, p)
    g2 = nxread(p)
    assert nx.is_isomorphic(g1, g2)
    assert nx.graph_edit_distance(g1, g2) == 0

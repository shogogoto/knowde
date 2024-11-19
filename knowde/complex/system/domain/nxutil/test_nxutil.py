"""networkx関連テスト."""


import networkx as nx

from knowde.complex.system.domain.nxutil import succ_attr, to_nested


def test_to_nested() -> None:  # noqa: D103
    g = nx.DiGraph()
    g.add_edge("sys", "h1", type="x")
    g.add_edge("h1", "h12", type="x")
    g.add_edge("h12", "h121", type="x")
    g.add_edge("h12", "h122", type="x")
    g.add_edge("sys", "h2", type="x")
    g.add_edge("sys", "dummy")
    assert to_nested(g, "sys", succ_attr("type", "x")) == {
        "h1": {
            "h12": {"h121": {}, "h122": {}},
        },
        "h2": {},
    }

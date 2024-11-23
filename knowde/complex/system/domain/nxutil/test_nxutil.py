"""networkx関連テスト."""


import networkx as nx
import pytest

from . import axiom_paths, filter_edge_attr, leaf_paths, succ_attr, to_nested


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


def test_filter_edge_attr() -> None:
    """特定の値を持ったedge attrで."""
    g = nx.DiGraph()
    nx.add_path(g, ["sys", *[f"a{i}" for i in range(2)]], type="A")
    nx.add_path(g, ["sys", *[f"b{i}" for i in range(2)]], type="B")
    sub = filter_edge_attr(g, "type", "A")
    assert list(nx.shortest_path(g, "sys", "b1")) == ["sys", "b0", "b1"]
    with pytest.raises(nx.NetworkXNoPath):
        nx.shortest_path(sub, "sys", "b1")


def test_leaf_paths() -> None:
    """終点となる要素までのpathsを取得."""
    # ╙── 0
    #     ├─╼ 1
    #     │   ├─╼ 4
    #     │   ├─╼ 5
    #     │   └─╼ 6
    #     ├─╼ 2
    #     │   ├─╼ 7
    #     │   ├─╼ 8
    #     │   └─╼ 9 ╼ dummy
    #     └─╼ 3
    #         ├─╼ 10
    #         ├─╼ 11
    #         └─╼ 12
    g = nx.balanced_tree(3, 2, nx.DiGraph())
    nx.set_edge_attributes(g, "x", "type")
    g.add_edge(9, "dummy", type="dummy")
    assert leaf_paths(g, 7, "x") == [[7]]
    assert leaf_paths(g, 2, "x") == [[2, 7], [2, 8], [2, 9]]
    assert leaf_paths(g, 2, "y") == []


def test_axiom_paths() -> None:
    """出発点となる要素までのpathsを取得."""
    g = nx.balanced_tree(3, 2, nx.DiGraph())
    nx.set_edge_attributes(g, "x", "type")
    g.add_edge(9, "dummy", type="dummy")
    assert axiom_paths(g, 7, "x") == [[0, 2, 7]]
    assert axiom_paths(g, 2, "x") == [[0, 2]]
    assert axiom_paths(g, "dummy", "x") == []

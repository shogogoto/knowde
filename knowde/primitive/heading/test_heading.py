"""test."""
from networkx import DiGraph

from knowde.core.nxutil import EdgeType
from knowde.primitive.heading import get_heading_path, get_headings


def test_get_headings() -> None:
    """見出し一覧."""
    root = "sys"
    g = DiGraph()
    EdgeType.HEAD.add_path(g, root, *[f"h{i}" for i in range(1, 4)])
    assert get_headings(g, root) == {root, *{f"h{i}" for i in range(1, 4)}}


def test_heading_path() -> None:
    """任意のnodeから直近の見出しpathを取得."""
    r = "root"
    g = DiGraph()
    g.add_node(r)
    EdgeType.HEAD.add_path(g, r, *[f"h{i}" for i in range(1, 4)])
    EdgeType.SIBLING.add_path(g, "h1", "aaa")
    EdgeType.BELOW.add_path(g, "aaa", "Aaa", "AAa")
    EdgeType.SIBLING.add_path(g, "h2", "bbb", "ccc")
    EdgeType.SIBLING.add_path(g, r, "x")
    # 隣接
    assert get_heading_path(g, r, "x") == [r]  # root直下
    assert get_heading_path(g, r, "aaa") == [r, "h1"]  # 見出しの兄弟
    # 非隣接
    assert get_heading_path(g, r, "Aaa") == [r, "h1"]  #   文の下
    assert get_heading_path(g, r, "AAa") == [r, "h1"]  #   文の下の下
    assert get_heading_path(g, r, "bbb") == [r, "h1", "h2"]
    assert get_heading_path(g, r, "ccc") == [r, "h1", "h2"]

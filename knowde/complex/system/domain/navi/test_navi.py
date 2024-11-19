"""test."""


from knowde.complex.system.domain.sysnet import (
    EdgeType,
    SystemNetwork,
)

from . import heading_path


def test_heading_path() -> None:
    """任意のnodeから直近の見出しpathを取得."""
    sn = SystemNetwork(root="sys")
    sn.add(EdgeType.HEAD, *[f"h{i}" for i in range(1, 4)])
    sn.add(EdgeType.SIBLING, "h1", "aaa")
    sn.add(EdgeType.BELOW, "aaa", "Aaa", "AAa")
    sn.add(EdgeType.SIBLING, "h2", "bbb", "ccc")
    sn.add(EdgeType.SIBLING, "x")
    # 隣接
    assert heading_path(sn, "x") == ["sys"]  # root直下
    assert heading_path(sn, "aaa") == ["sys", "h1"]  # 見出しの兄弟
    # 非隣接
    assert heading_path(sn, "Aaa") == ["sys", "h1"]  #   文の下
    assert heading_path(sn, "AAa") == ["sys", "h1"]  #   文の下の下
    assert heading_path(sn, "bbb") == ["sys", "h1", "h2"]
    assert heading_path(sn, "ccc") == ["sys", "h1", "h2"]

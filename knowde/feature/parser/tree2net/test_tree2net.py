"""test."""


from knowde.core.nxutil import EdgeType, to_nested
from knowde.feature.parser.tree2net import parse2net
from knowde.primitive.heading import get_heading_path


def test_add_heading() -> None:
    """headingを正しく取得できる."""
    _s = """
        # h1
            aaa
            bbb
                ccc
                    -> ddd
        ## h2
            fff
            ggg
        ### h3
            hhh
                iii
    """
    sn = parse2net(_s)
    assert get_heading_path(sn.g, sn.root, "ccc") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "ddd") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "ggg") == ["# h1", "## h2"]
    assert get_heading_path(sn.g, sn.root, "iii") == ["# h1", "## h2", "### h3"]


def test_add_ctx() -> None:
    """用語解決."""
    _s = """
        # h1
            aaa
                <-> anti aaa\
                        bbb
            B: bbb
            C{B}: ccc
                -> D: d{CB}d
                    vvv
                    www
                    -> xxx
    """

    sn = parse2net(_s)
    assert list(EdgeType.SIBLING.succ(sn.g, "bbb")) == ["ccc"]
    assert list(EdgeType.TO.succ(sn.g, "ccc")) == ["d{CB}d"]
    assert list(EdgeType.SIBLING.succ(sn.g, "ccc")) == []

    assert list(EdgeType.TO.pred(sn.g, "d{CB}d")) == ["ccc"]
    assert to_nested(sn.g, "d{CB}d", EdgeType.SIBLING.succ) == {"vvv": {"www": {}}}
    assert list(EdgeType.TO.succ(sn.g, "d{CB}d")) == ["xxx"]

    assert list(EdgeType.ANTI.succ(sn.g, "aaa")) == ["anti aaabbb"]
    assert list(EdgeType.ANTI.pred(sn.g, "anti aaabbb")) == ["aaa"]

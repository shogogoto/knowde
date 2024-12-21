"""test."""


import pytest

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
                eee
        ## h2
            fff
            ggg
                -> ddd
        ### h3
            hhh
                iii
                <- jjj
    """
    sn = parse2net(_s)
    assert get_heading_path(sn.graph, sn.root, "ccc") == ["# h1"]
    assert get_heading_path(sn.graph, sn.root, "ddd") == ["# h1", "## h2"]
    assert get_heading_path(sn.graph, sn.root, "iii") == ["# h1", "## h2", "### h3"]
    assert get_heading_path(sn.graph, sn.root, "jjj") == ["# h1", "## h2", "### h3"]


# def test_sibling() -> None:
#     """兄弟追加."""


@pytest.mark.skip()
def test_add_ctx() -> None:
    """文脈."""
    _s = """
        # h1
            aaa
                <-> anti aaa\
                        aaa
            B: bbb
            C{B}: ccc
                -> D: d{CB}d
                    vvv
                    www
                    <- xxx
    """

    sn = parse2net(_s)
    assert list(EdgeType.SIBLING.succ(sn.graph, "bbb")) == ["ccc"]
    assert list(EdgeType.TO.succ(sn.graph, "ccc")) == ["d{CB}d"]
    assert list(EdgeType.SIBLING.succ(sn.graph, "ccc")) == []

    assert list(EdgeType.TO.pred(sn.graph, "d{CB}d")) == ["ccc"]
    assert to_nested(sn.graph, "d{CB}d", EdgeType.SIBLING.succ) == {"vvv": {"www": {}}}
    assert list(EdgeType.TO.succ(sn.graph, "d{CB}d")) == ["xxx"]

    assert list(EdgeType.ANTI.succ(sn.graph, "aaa")) == ["anti aaaaaa"]
    assert list(EdgeType.ANTI.pred(sn.graph, "anti aaaaaa")) == ["aaa"]


@pytest.mark.skip()
def test_replace_quoterm() -> None:
    """引用用語."""
    _s = """
        # h1
            A: aaa
            B: bbb
        ## h2
            `A`
                ccc
                ddd
    """

    sn = parse2net(_s)
    assert sn.quoterms == ["`A`"]
    sn.replace_quoterms()
    assert to_nested(sn.graph, "aaa", EdgeType.SIBLING.succ) == {
        "bbb": {},
        "ccc": {"ddd": {}},
    }


def test_multiline_def() -> None:
    """改行付き定義."""

"""関係集合test."""


from knowde.complex.__core__.tree2net import parse2graph
from knowde.primitive.__core__.nxutil import to_nested
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.heading import get_heading_path, get_headings


def test_add_block() -> None:
    """blockを正しく配置."""
    _s = """
        # h1
            1
            2
                21
            3
                31
                32
            4
                41
                42
                    421
                43
                    431
                    432
                44
                    441
                    442
                        4421
                        4422
                        4423
    """
    g = parse2graph(_s)
    assert list(EdgeType.BELOW.succ(g, "# h1")) == ["1"]
    assert to_nested(g, "1", EdgeType.SIBLING.succ) == {"2": {"3": {"4": {}}}}
    assert list(EdgeType.BELOW.succ(g, "2")) == ["21"]
    assert to_nested(g, "21", EdgeType.SIBLING.succ) == {}
    assert list(EdgeType.BELOW.succ(g, "3")) == ["31"]
    assert to_nested(g, "31", EdgeType.SIBLING.succ) == {"32": {}}
    assert list(EdgeType.BELOW.succ(g, "4")) == ["41"]
    assert to_nested(g, "41", EdgeType.SIBLING.succ) == {"42": {"43": {"44": {}}}}
    assert list(EdgeType.BELOW.succ(g, "42")) == ["421"]
    assert to_nested(g, "421", EdgeType.SIBLING.succ) == {}
    assert list(EdgeType.BELOW.succ(g, "43")) == ["431"]
    assert list(EdgeType.BELOW.succ(g, "44")) == ["441"]
    assert to_nested(g, "441", EdgeType.SIBLING.succ) == {"442": {}}
    assert list(EdgeType.BELOW.succ(g, "442")) == ["4421"]
    assert to_nested(g, "4421", EdgeType.SIBLING.succ) == {"4422": {"4423": {}}}


def test_add_heading() -> None:
    """headingを正しく取得できる."""
    _s = """
        !c00
        # h1
        !c0
            aaa
        !c1
            bbb
                ccc
                eee
                !c2
                    eEE
        !c2
                    eeE
        ## h2
        !c3
            fff
            ggg
                -> ddd
        ### h3
            hhh
                iii
                <- jjj
    """
    g = parse2graph(_s)
    root = "# h1"
    assert get_headings(g, root) == {"# h1", "## h2", "### h3"}
    assert get_heading_path(g, root, "ccc") == ["# h1"]
    assert get_heading_path(g, root, "eEE") == ["# h1"]
    assert get_heading_path(g, root, "eeE") == ["# h1"]
    assert get_heading_path(g, root, "ddd") == ["# h1", "## h2"]
    assert get_heading_path(g, root, "iii") == ["# h1", "## h2", "### h3"]
    assert get_heading_path(g, root, "jjj") == ["# h1", "## h2", "### h3"]


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
    """

    g = parse2graph(_s)
    assert list(EdgeType.SIBLING.succ(g, "bbb")) == ["ccc"]
    assert list(EdgeType.TO.succ(g, "ccc")) == ["d{CB}d"]
    assert list(EdgeType.SIBLING.succ(g, "ccc")) == []
    assert list(EdgeType.TO.pred(g, "d{CB}d")) == ["ccc"]
    assert to_nested(g, "d{CB}d", EdgeType.BELOW.succ) == {"vvv": {}}
    assert to_nested(g, "vvv", EdgeType.SIBLING.succ) == {"www": {}}
    # 両方向
    assert list(EdgeType.ANTI.succ(g, "aaa")) == ["anti aaaaaa"]
    assert list(EdgeType.ANTI.pred(g, "anti aaaaaa")) == ["aaa"]


def test_replace_quoterm() -> None:
    """引用用語."""
    _s = """
        # h1
            A: aaa
                aAA
                aBB
            B: bbb
        ## h2
            `A`
                ccc
                ddd
    """

    g = parse2graph(_s)
    assert to_nested(g, "aaa", EdgeType.SIBLING.succ) == {"bbb": {}}
    # belowを1つに統合しようと思ったけどやめた
    assert to_nested(g, "aaa", EdgeType.BELOW.succ) == {
        "aAA": {},
        "ccc": {},
    }

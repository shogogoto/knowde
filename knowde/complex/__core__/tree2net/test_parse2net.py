"""用語関連."""


from knowde.complex.__core__.tree2net import parse2net
from knowde.primitive.__core__.nxutil import to_nested
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.heading import get_heading_path, get_headings


def test_duplicable() -> None:
    """重複可能な文."""
    _s = r"""
        # h1
            1
                +++ dup1 +++
                +++ dup1 +++
                +++ dup1 +++
            2
    """
    _sn = parse2net(_s)


def test_add_resolved_edge() -> None:
    """parse2net版."""
    _s = r"""
        # h1
            A: df
            B: b{A}b
            C{B}: ccc
            D: d{CB}d
        ## h2
            P{D}: ppp
            Q: qqq
            X:
    """
    sn = parse2net(_s)
    assert sn.get_resolved("df") == {}
    assert sn.get_resolved("b{A}b") == {"df": {}}
    assert sn.get_resolved("ccc") == {"b{A}b": {"df": {}}}
    assert sn.get_resolved("d{CB}d") == {"ccc": {"b{A}b": {"df": {}}}}
    assert sn.get_resolved("ppp") == {"d{CB}d": {"ccc": {"b{A}b": {"df": {}}}}}
    assert sn.get_resolved("qqq") == {}


def test_multiline() -> None:
    r"""\改行を1行に."""
    _s = r"""
        # 1
            aaa\
                bbb
    """
    _t = parse2net(_s)
    assert "aaabbb" in _t.g


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
    sn = parse2net(_s)
    assert list(EdgeType.BELOW.succ(sn.g, sn.root)) == ["1"]
    assert to_nested(sn.g, "1", EdgeType.SIBLING.succ) == {"2": {"3": {"4": {}}}}
    assert list(EdgeType.BELOW.succ(sn.g, "2")) == ["21"]
    assert to_nested(sn.g, "21", EdgeType.SIBLING.succ) == {}
    assert list(EdgeType.BELOW.succ(sn.g, "3")) == ["31"]
    assert to_nested(sn.g, "31", EdgeType.SIBLING.succ) == {"32": {}}
    assert list(EdgeType.BELOW.succ(sn.g, "4")) == ["41"]
    assert to_nested(sn.g, "41", EdgeType.SIBLING.succ) == {"42": {"43": {"44": {}}}}
    assert list(EdgeType.BELOW.succ(sn.g, "42")) == ["421"]
    assert to_nested(sn.g, "421", EdgeType.SIBLING.succ) == {}
    assert list(EdgeType.BELOW.succ(sn.g, "43")) == ["431"]
    assert list(EdgeType.BELOW.succ(sn.g, "44")) == ["441"]
    assert to_nested(sn.g, "441", EdgeType.SIBLING.succ) == {"442": {}}
    assert list(EdgeType.BELOW.succ(sn.g, "442")) == ["4421"]
    assert to_nested(sn.g, "4421", EdgeType.SIBLING.succ) == {"4422": {"4423": {}}}


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
    sn = parse2net(_s)
    assert get_headings(sn.g, sn.root) == {"# h1", "## h2", "### h3"}
    assert get_heading_path(sn.g, sn.root, "ccc") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "eEE") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "eeE") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "ddd") == ["# h1", "## h2"]
    assert get_heading_path(sn.g, sn.root, "iii") == ["# h1", "## h2", "### h3"]
    assert get_heading_path(sn.g, sn.root, "jjj") == ["# h1", "## h2", "### h3"]


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

    sn = parse2net(_s)
    assert list(EdgeType.SIBLING.succ(sn.g, "bbb")) == ["ccc"]
    assert list(EdgeType.TO.succ(sn.g, "ccc")) == ["d{CB}d"]
    assert list(EdgeType.SIBLING.succ(sn.g, "ccc")) == []
    assert list(EdgeType.TO.pred(sn.g, "d{CB}d")) == ["ccc"]
    assert to_nested(sn.g, "d{CB}d", EdgeType.BELOW.succ) == {"vvv": {}}
    assert to_nested(sn.g, "vvv", EdgeType.SIBLING.succ) == {"www": {}}
    # 両方向
    assert list(EdgeType.ANTI.succ(sn.g, "aaa")) == ["anti aaaaaa"]
    assert list(EdgeType.ANTI.pred(sn.g, "anti aaaaaa")) == ["aaa"]


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

    sn = parse2net(_s)
    assert to_nested(sn.g, "aaa", EdgeType.SIBLING.succ) == {"bbb": {}}
    # belowを1つに統合しようと思ったけどやめた
    assert to_nested(sn.g, "aaa", EdgeType.BELOW.succ) == {
        "aAA": {},
        "ccc": {},
    }


def test_template() -> None:
    """テンプレート."""
    _s = r"""
        # h1
            f<a,b>: \diff{a, b}
            g<a>: !a!
            call g<a> -> _g<f<a, 1>>_
    """
    _sn = parse2net(_s)
    ret = [_sn.expand(s) for s in _sn.sentences]
    assert ret == [r"call g<a> -> !\diff{a, 1}!"]

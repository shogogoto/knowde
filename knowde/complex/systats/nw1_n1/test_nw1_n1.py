"""netwok1 node1 getter."""


from pytest_unordered import unordered

from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.systats.nw1_n1 import (
    get_conclusion,
    get_details,
    get_parent_or_none,
    get_premise,
    get_refer,
    get_referred,
    has_dependency,
    recursively_nw1n1,
)


def test_get_detail_parent() -> None:
    """詳細."""
    _s = r"""
        # h1
            aaa
            B: bbb
                b1
                b2
                    b21
                    b22
        ## h2
            ccc
                c1
                c2
            `B`
                1b
                2b
    """
    _sn = parse2net(_s)
    assert get_details(_sn, "aaa") == []
    assert get_details(_sn, "bbb") == [["b1", "b2"], ["1b", "2b"]]

    assert get_parent_or_none(_sn, "aaa") is None
    assert get_parent_or_none(_sn, "b2") == "bbb"
    assert get_parent_or_none(_sn, "b21") == "b2"
    assert get_parent_or_none(_sn, "# h1") is None
    assert get_parent_or_none(_sn, "## h2") is None


def test_has_dependency() -> None:
    """意味的な依存を持つ."""
    _s = r"""
        # h1
        ## h2
        ### h3
            aaa
                -> bbb
                <- 000
                <-> ccc
                e.g. ddd
                when. 1919
                where. japan
                ~= eee
                g.e. fff
                by. x-men
            bro
                little
    """
    _sn = parse2net(_s)
    assert has_dependency(_sn, "aaa")
    assert not has_dependency(_sn, "bro")


def test_refer_referred() -> None:
    """用語引用."""
    _s = r"""
        # h1
            A: aaa
            B: b{A}b
            C: c{A}c
            D: d{C}d
            E{D}: eee
    """
    sn = parse2net(_s)
    assert get_refer(sn, "aaa") == unordered(
        [
            Def.create("b{A}b", ["B"]),
            Def.create("c{A}c", ["C"]),
        ],
    )
    assert get_refer(sn, "b{A}b") == []
    assert get_refer(sn, "c{A}c") == [Def.create("d{C}d", ["D"])]
    assert get_refer(sn, "d{C}d") == [Def.create("eee", ["E{D}"])]
    assert get_refer(sn, "eee") == []

    assert get_referred(sn, "aaa") == []
    assert get_referred(sn, "b{A}b") == [Def.create("aaa", ["A"])]
    assert get_referred(sn, "c{A}c") == [Def.create("aaa", ["A"])]
    assert get_referred(sn, "d{C}d") == [Def.create("c{A}c", ["C"])]
    assert get_referred(sn, "eee") == [Def.create("d{C}d", ["D"])]


def test_premise_conclusion() -> None:
    """用語引用."""
    _s = r"""
        # h1
            aaa
                -> A| bbb
                <- 000
                <-> ccc
            bro
                little
            `A`
                -> ddd

    """
    sn = parse2net(_s)
    assert get_premise(sn, "bbb") == ["aaa"]
    assert get_conclusion(sn, "bbb") == ["ddd"]


def test_recursively() -> None:
    """再帰的取得."""
    _s = r"""
        # h1
            aaa
                -> bbb
                -> ccc
                    -> ddd
                        -> eee
                    -> fff
                -> ggg
    """
    sn = parse2net(_s)
    f1 = recursively_nw1n1(get_conclusion, 1)
    assert f1(sn, "aaa") == ["bbb", "ccc", "ggg"]
    f2 = recursively_nw1n1(get_conclusion, 2)
    assert f2(sn, "aaa") == [["bbb", []], ["ccc", ["ddd", "fff"]], ["ggg", []]]
    f3 = recursively_nw1n1(get_conclusion, 3)
    assert f3(sn, "aaa") == [
        ["bbb", []],
        ["ccc", [["ddd", ["eee"]], ["fff", []]]],
        ["ggg", []],
    ]
    for i in range(4, 7):
        f4 = recursively_nw1n1(get_conclusion, i)
        assert f4(sn, "aaa") == [
            ["bbb", []],
            ["ccc", [["ddd", [["eee", []]]], ["fff", []]]],
            ["ggg", []],
        ]

"""netwok1 node1 getter."""

from pytest_unordered import unordered

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.systats.nw1_n1 import (
    get_conclusion,
    get_detail,
    get_example,
    get_general,
    get_parent_or_none,
    get_premise,
    get_refer,
    get_referred,
    has_dependency,
    recursively_nw1n1,
)


def test_get_detail_parent() -> None:
    """詳細."""
    s = r"""
        # h1
            aaa
            B: bbb
                b1
                b2
                    b21
                    b22
                    b23
        ## h2
            ccc
                c1
                c2
            `B`
                1b
                2b
    """
    sn = parse2net(s)
    assert get_detail(sn, "aaa") == []
    assert get_detail(sn, "bbb") == ["b1", "b2", "1b", "2b"]

    assert get_parent_or_none(sn, "aaa") is None
    assert get_parent_or_none(sn, "b2") == "bbb"
    assert get_parent_or_none(sn, "b21") == "b2"
    assert get_parent_or_none(sn, "b22") == "b2"
    assert get_parent_or_none(sn, "b23") == "b2"
    assert get_parent_or_none(sn, "# h1") is None
    assert get_parent_or_none(sn, "## h2") is None


def test_has_dependency() -> None:
    """意味的な依存を持つ."""
    s = r"""
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
    sn = parse2net(s)
    assert has_dependency(sn, "aaa")
    assert not has_dependency(sn, "bro")


def test_refer_referred() -> None:
    """用語引用."""
    s = r"""
        # h1
            A: aaa
            B: b{A}b
            C: c{A}c
            D: d{C}d
            E{D}: eee
    """
    sn = parse2net(s)
    assert get_refer(sn, "aaa") == unordered(["b{A}b", "c{A}c"])
    assert get_refer(sn, "b{A}b") == []
    assert get_refer(sn, "c{A}c") == ["d{C}d"]
    assert get_refer(sn, "d{C}d") == ["eee"]
    assert get_refer(sn, "eee") == []

    assert get_referred(sn, "aaa") == []
    assert get_referred(sn, "b{A}b") == ["aaa"]
    assert get_referred(sn, "c{A}c") == ["aaa"]
    assert get_referred(sn, "d{C}d") == ["c{A}c"]
    assert get_referred(sn, "eee") == ["d{C}d"]


def test_premise_conclusion() -> None:
    """用語引用."""
    s = r"""
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
    sn = parse2net(s)
    assert get_premise(sn, "bbb") == ["aaa"]
    assert get_conclusion(sn, "bbb") == ["ddd"]


def test_example_general() -> None:
    """具体抽象."""
    s = r"""
        # h1
            aaa
                ex. a1
                ex. a2
                    ex. a21
                    ex. a22
                    ex. a23
    """
    sn = parse2net(s)
    assert get_example(sn, "aaa") == ["a1", "a2"]
    assert get_general(sn, "a22") == ["a2"]


def test_recursively() -> None:
    """再帰的取得."""
    s = r"""
        # h1
            aaa
                -> bbb
                -> ccc
                    -> ddd
                        -> eee
                    -> fff
                -> ggg
    """
    sn = parse2net(s)
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


def test_get_detail_recursively() -> None:
    """詳細の再帰的取得."""
    s = r"""
        # h
            1
                11
                    21
                        31
                        32
                    22
                        33
                        34
                            41
                            42
                12

    """
    sn = parse2net(s)
    f1 = recursively_nw1n1(get_detail, 1)
    assert f1(sn, "1") == ["11", "12"]
    f2 = recursively_nw1n1(get_detail, 3)
    assert f2(sn, "1") == [
        ["11", [["21", ["31", "32"]], ["22", ["33", "34"]]]],
        ["12", []],
    ]


def test_get_refer_recursively() -> None:
    """referの再帰的取得."""
    s = r"""
        # h
            A: aaa
            B: b{A}
            C: c{B}
            D: d{C}
            E: e{D}
            F: f{E}
            G: g{F}
    """
    sn = parse2net(s)
    f1 = recursively_nw1n1(get_refer, 1)
    assert f1(sn, "aaa") == ["b{A}"]
    f2 = recursively_nw1n1(get_refer, 3)
    assert f2(sn, "aaa") == [["b{A}", [["c{B}", ["d{C}"]]]]]
    f3 = recursively_nw1n1(get_refer, 5)
    assert f3(sn, "aaa") == [["b{A}", [["c{B}", [["d{C}", [["e{D}", ["f{E}"]]]]]]]]]

"""test."""

from pytest_unordered import unordered

from knowde.feature.parsing.tree2net import parse2net

from .domain import (
    get_axiom,
    get_isolation,
    get_unrefered,
)


def test_get_isolation() -> None:
    """孤立したノード."""
    s = r"""
        # h1
            aaa
            B: bbb
                B1: bbb1
                bbb2
                bbb3
            ccc{B}
            `B`
                below2
                below3
            eee{B}
            fff
            G{B}: ggg
    """
    sn_ = parse2net(s)
    assert get_isolation(sn_) == unordered(["aaa", "fff"])

    s = r"""
        # h1
            A: aaa
            B: bbb{A}
            ccc{B}
            eee{B}
            fff
            G{B}: ggg
    """
    sn = parse2net(s)
    assert sn.get_resolved("ggg") == {"bbb{A}": {"aaa": {}}}
    assert get_isolation(sn) == ["fff"]


def test_get_axioms() -> None:
    """axiom取得."""
    s = r"""
        # h1
            A: aaa
            B: bbb{A}
                B1: bbb1
                bbb2
                    -> X| xxx
                bbb3
            ccc{B}
            `B`
                below2
                below3
                    <- xyz
                        <- abc
                +++x+++
            eee{B}
            fff
    """
    sn = parse2net(s)
    assert get_axiom(sn) == unordered(["bbb2", "abc"])
    assert get_unrefered(sn) == ["aaa"]

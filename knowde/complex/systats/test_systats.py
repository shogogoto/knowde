"""test."""


from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.systats import (
    get_axiom_resolved,
    get_axiom_to,
    get_isolation,
)


def test_get_isolation() -> None:
    """孤立したノード."""
    _s = r"""
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
    _sn = parse2net(_s)
    assert get_isolation(_sn) == ["aaa", "fff"]

    _s = r"""
        # h1
            A: aaa
            B: bbb{A}
            ccc{B}
            eee{B}
            fff
            G{B}: ggg
    """
    sn = parse2net(_s)
    assert sn.get_resolved("ggg") == {"bbb{A}": {"aaa": {}}}
    assert get_isolation(sn) == ["fff"]


def test_get_axioms() -> None:
    """axiom取得."""
    _s = r"""
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
    sn = parse2net(_s)
    assert get_axiom_to(sn) == ["bbb2", "abc"]
    assert get_axiom_resolved(sn) == [Def.create("aaa", ["A"])]

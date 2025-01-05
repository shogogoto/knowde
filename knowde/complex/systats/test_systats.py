"""test."""


import pytest

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.systats import (
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


@pytest.mark.skip()
def test_n_nodes() -> None:
    """node数."""
    _s = r"""
        # h1
            A: aaa
            B: bbb{A}
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
    # print("#" * 80)
    sn = parse2net(_s)

    # print(to_nested(sn.g, "ggg", EdgeType.RESOLVED.succ))
    # print(to_nested(sn.g, "ggg", EdgeType.RESOLVED.pred))
    # nxprint(sn.g, True)
    assert sn.get_resolved("ggg") == {"bbb": {}}
    # nxprint(_sn.g, True)
    # print("#" * 80)
    # print(get_systats(_sn))

"""test."""


import pytest

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.system.systats import (
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
    _sn.add_resolved_edges()
    _sn.replace_quoterms()
    get_isolation(_sn)
    # assert get_isolation(_sn) == ["aaa", "fff"]


@pytest.mark.skip()
def test_n_nodes() -> None:
    """node数."""
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
    _sn.add_resolved_edges()
    _sn.replace_quoterms()
    # print("#" * 80)
    # print(get_systats(_sn))
    # print(n_axiom(_sn))

    # nxprint(_sn.g, True)

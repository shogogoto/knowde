"""test."""

import pytest
from pytest_unordered import unordered

from knowde.complex.nxdb import LSentence
from knowde.feature.knowde.detail import detail_knowde
from knowde.feature.knowde.repo import save_text
from knowde.primitive.__core__.nxutil import to_leaves, to_roots
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.user.repo import LUser


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser(email="onex@gmail.com").save()


def test_detail(u: LUser):
    """IDによる詳細."""
    s = """
    # titleX
    ## head1
    ### head2
        zero, re :0
            when. R10/11/11
            xxx
                x1
                    x11
                    x12
                x2
                    x21
                    x22
                    x23
                        x231
            yyy
            zzz
            <- -1
                when. 1919
                <- -11
                <- -12
            <- -2
                <- -21
                <- -22
            -> 1
                -> 11
                -> 12
            -> 2
                -> 21
                -> 22
                    -> 221
        A: a
        B: b{A}b{zero}
        C: c{B}c
            -> ccc
    """
    _sn, _r = save_text(u.uid, s)
    s = LSentence.nodes.get(val="0")
    detail = detail_knowde(s.uid)
    assert to_roots(detail.g, EdgeType.TO) == unordered(["-11", "-12", "-21", "-22"])
    assert to_leaves(detail.g, EdgeType.TO) == unordered(["11", "12", "21", "221"])
    assert to_roots(detail.g, EdgeType.RESOLVED) == unordered(["c{B}c"])
    assert to_leaves(detail.g, EdgeType.RESOLVED) == unordered(["0", "a"])

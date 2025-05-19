"""test."""

from uuid import UUID

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
    return LUser(email="onex@gmail.com", hashed_password="xxx").save()  # noqa: S106


def test_detail(u: LUser):
    """IDによる詳細."""
    s = """
    # titleX
    ## head1
    ### head2
        parent
            when. 19C
            p1
            p2
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
    _sn, _r = save_text(u.uid, s, path=("A", "B", "C.txt"))  # C.txtはDBには格納されない
    s = LSentence.nodes.get(val="0")
    detail = detail_knowde(UUID(s.uid))
    # assert list(EdgeType.TO.succ(detail.g, "0")) == unordered(["1", "2"])
    assert [k.sentence for k in detail.succ("0", EdgeType.TO)] == unordered(["1", "2"])
    roots_to = to_roots(detail.g, EdgeType.TO)
    assert [detail.knowdes[UUID(s)].sentence for s in roots_to] == unordered([
        "-11",
        "-12",
        "-21",
        "-22",
    ])
    leaves_to = to_leaves(detail.g, EdgeType.TO)
    assert [detail.knowdes[UUID(s)].sentence for s in leaves_to] == unordered([
        "11",
        "12",
        "21",
        "221",
    ])
    roots_ref = to_roots(detail.g, EdgeType.RESOLVED)
    leaves_ref = to_leaves(detail.g, EdgeType.RESOLVED)
    assert [detail.knowdes[UUID(s)].sentence for s in roots_ref] == unordered([
        "c{B}c",
    ])

    assert [detail.knowdes[UUID(s)].sentence for s in leaves_ref] == unordered([
        "0",
        "a",
    ])

    loc = detail.location
    assert loc.user.uid == UUID(u.uid)
    assert [f.val for f in loc.folders] == ["A", "B"]
    assert loc.resource.name == "# titleX"
    assert [f.val for f in loc.headers] == ["## head1", "### head2"]
    assert [str(p) for p in loc.parents] == [
        "parentT(19C)",
        "p1",
        "p2",
        "0[zero(re)]T(R10/11/11)",
    ]

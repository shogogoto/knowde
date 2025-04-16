"""test.

誰でも見れる


register user
knowde search


sync
"""

import pytest
from pytest_unordered import unordered

from knowde.complex.nxdb.restore import restore_sysnet
from knowde.feature.knowde.repo import get_stats_by_id, save_text, search_knowde
from knowde.primitive.user.repo import LUser


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser(email="onex@gmail.com").save()


def test_get_knowde_attrs(u: LUser):
    """文の所属などを取得."""
    s = """
    # titleX
        @author John Due
        @published H20/11/1
    ## h11
        A, A1, A2: a
            when. 20C
            -> P: aaa
            aaaa
        B: bA123
        A11, TNTN: ちん
        D: bbbaaaaa
    ## h12
        x: xxx
        y: {x}yy
    """
    _sn, _ = save_text(u.uid, s)
    adjs = search_knowde("A1")
    assert [a.center.sentence for a in adjs] == unordered(["a", "ちん", "bA123"])

    adjs = search_knowde("xxx")
    assert adjs[0].referreds[0].sentence == "{x}yy"
    # adjs = search_knowde("y")
    # assert adjs[0].refers[0].sentence == "xxx"


def test_stats_from_db(u: LUser):
    """systats相当のものをDBから取得する."""
    s = """
    # titleX
        0
            <- -1
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
        B: b{A}b
        C: c{B}c
            -> ccc
        detail
            d1
            d2
            d3
                d31
                d32

    """
    _, r = save_text(u.uid, s)
    _sn, uids = restore_sysnet(r.uid)
    assert get_stats_by_id(uids["0"]) == [6, 7, 2, 3, 0, 0, 0]
    assert get_stats_by_id(uids["1"]) == [7, 2, 3, 1, 0, 0, 0]
    assert get_stats_by_id(uids["a"]) == [0, 0, 0, 0, 2, 0, 0]
    assert get_stats_by_id(uids["b{A}b"]) == [0, 0, 0, 0, 1, 1, 0]
    assert get_stats_by_id(uids["detail"]) == [0, 0, 0, 0, 0, 0, 5]

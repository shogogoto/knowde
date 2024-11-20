"""test deduction stats."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde.complex.deduction.proposition.repo.repo import add_proposition
from knowde.complex.deduction.repo.deduction import deduct
from knowde.complex.deduction.repo.statistics import find_deductstats

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.complex.deduction.proposition.domain import Proposition


def _uids(*ps: Proposition) -> list[UUID]:
    return [p.valid_uid for p in ps]


def test_no_chain() -> None:
    """連結していない演繹."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    p4 = add_proposition("p4")
    c = add_proposition("conclusion")
    txt = "これこれよりQED"
    d = deduct(txt, _uids(p1, p2, p3, p4), c.valid_uid)
    st = find_deductstats(d.valid_uid)
    assert st.nums == (4, 1, 4, 1, 1, 1)


def test_2chain() -> None:
    """連結した演繹."""
    p11 = add_proposition("p11")
    p12 = add_proposition("p12")
    p13 = add_proposition("p13")
    c1 = add_proposition("c1")
    d1 = deduct("d1", _uids(p11, p12, p13), c1.valid_uid)
    p22 = add_proposition("p22")
    p23 = add_proposition("p23")
    c2 = add_proposition("c2")
    d2 = deduct("d2", _uids(c1, p22, p23), c2.valid_uid)
    p32 = add_proposition("p32")
    c3 = add_proposition("c3")
    d3 = deduct("d3", _uids(c2, p32), c3.valid_uid)

    st1 = find_deductstats(d1.valid_uid)
    st2 = find_deductstats(d2.valid_uid)
    st3 = find_deductstats(d3.valid_uid)
    assert st1.nums == (3, 3, 3, 1, 1, 3)
    assert st2.nums == (6, 2, 5, 1, 2, 2)
    assert st3.nums == (8, 1, 6, 1, 3, 1)

"""論証のテスト."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_unordered import unordered

from knowde.feature.proposition.repo.deduction import deduct, list_deductions
from knowde.feature.proposition.repo.proposition import add_proposition

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.feature.proposition.domain import Proposition


def _uids(*ps: Proposition) -> list[UUID]:
    return [p.valid_uid for p in ps]


def test_simple_add() -> None:
    """1つの命題を前提."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    p4 = add_proposition("p4")
    p5 = add_proposition("p5")
    p6 = add_proposition("p6")
    p7 = add_proposition("p7")
    c = add_proposition("conclusion")
    txt = "QED"
    d = deduct(txt, _uids(p1, p2, p3, p4, p5, p6, p7), c.valid_uid)
    assert list_deductions().deductions == [d]


def test_2chain() -> None:
    """1つの定義を前提."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    p4 = add_proposition("p4")
    d1 = deduct("xxx", _uids(p1, p2), p3.valid_uid)
    d2 = deduct("yyy", [p3.valid_uid], p4.valid_uid)
    assert list_deductions().deductions == unordered([d1, d2])

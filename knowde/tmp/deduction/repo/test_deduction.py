"""論証のテスト."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_unordered import unordered

from knowde.tmp.deduction.proposition.repo.repo import add_proposition
from knowde.tmp.deduction.repo.deduction import (
    deduct,
    find_deduction_by_uid,
    list_deductions,
    replace_conclusion,
    replace_premises,
)
from knowde.tmp.deduction.repo.errors import (
    CyclicDependencyError,
    NoPremiseError,
    PremiseDuplicationError,
)

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.tmp.deduction.domain import Proposition


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


def test_refuse_cyclic_deps() -> None:
    """前提と結論が重複."""
    p = add_proposition("p1")
    with pytest.raises(CyclicDependencyError):
        deduct("xxx", _uids(p), p.valid_uid)


def test_common_premise_and_conclusion() -> None:
    """前提と同じ結論は許されない."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p1")
    with pytest.raises(PremiseDuplicationError):
        deduct("xxx", _uids(p1, p1), p2.valid_uid)


def test_replace_premises() -> None:
    """前提の入れ替え."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    d1 = deduct("xxx", _uids(p1, p2), p3.valid_uid)
    assert d1.premises == [p1, p2]
    assert d1.conclusion == p3

    p4 = add_proposition("p4")
    p5 = add_proposition("p5")
    d2 = replace_premises(d1.valid_uid, _uids(p4, p5))
    assert d1.valid_uid == d2.valid_uid
    assert d2.premises == [p4, p5]
    assert d2.conclusion == p3


def test_no_premise() -> None:
    """前提がない場合エラー."""
    p = add_proposition("p1")
    with pytest.raises(NoPremiseError):
        deduct("xxx", [], p.valid_uid)


def test_replace_conclusion() -> None:
    """結論の入れ替え."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    d1 = deduct("xxx", _uids(p1, p2), p3.valid_uid)

    p4 = add_proposition("p4")
    d2 = replace_conclusion(d1.valid_uid, p4.valid_uid)
    assert d1.valid_uid == d2.valid_uid
    assert d1.premises == d2.premises
    assert d2.conclusion == p4


def test_find_deduction() -> None:
    """前提と結論を含めた演繹の検索."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    d = deduct("xxx", _uids(p1, p2), p3.valid_uid)
    assert d == find_deduction_by_uid(d.valid_uid)

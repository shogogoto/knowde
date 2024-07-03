"""論証のテスト."""


from pytest_unordered import unordered

from knowde.feature.proposition.repo.deduction import deduct, list_deductions
from knowde.feature.proposition.repo.proposition import add_proposition


def test_simple_add() -> None:
    """1つの命題を前提."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    p4 = add_proposition("p4")
    c = add_proposition("conclusion")
    txt = "これこれよりQED"
    d = deduct(
        txt,
        [p1.valid_uid, p2.valid_uid, p3.valid_uid, p4.valid_uid],
        c.valid_uid,
    )
    assert d.premises == [p1, p2, p3, p4]
    assert d.conclusion == c
    assert d.text == txt


def test_2chain() -> None:
    """1つの定義を前提."""
    p1 = add_proposition("p1")
    p2 = add_proposition("p2")
    p3 = add_proposition("p3")
    p4 = add_proposition("p4")
    d1 = deduct("xxx", [p1.valid_uid, p2.valid_uid], p3.valid_uid)
    d2 = deduct("yyy", [p3.valid_uid], p4.valid_uid)
    assert list_deductions() == unordered([d1, d2])

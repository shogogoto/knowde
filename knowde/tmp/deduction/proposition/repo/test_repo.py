"""test."""
from knowde.tmp.deduction.proposition.repo.repo import (
    add_proposition,
    change_proposition,
    delete_proposition,
    list_propositions,
)


def test_crud_prop() -> None:
    """CRUD."""
    p1 = add_proposition("prop1")
    assert list_propositions() == [p1]
    p2 = change_proposition(p1.valid_uid, "prop2")
    assert p1.valid_uid == p2.valid_uid
    assert p2.text == "prop2"
    delete_proposition(p2.valid_uid)
    assert list_propositions() == []

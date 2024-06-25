"""命題test."""


from knowde.feature.proposition.repo.proposition import (
    add_proposition,
    change_proposition,
    delete_proposition,
    list_propositions,
)


def crud_prop() -> None:
    """CRUD."""
    p1 = add_proposition("prop1")
    assert list_propositions() == [p1]
    p2 = change_proposition(p1.valid_uid, "prop2")
    assert p1.valid_uid == p2.valid_uid
    assert p2.value == "prop2"
    delete_proposition(p2.valid_uid)
    assert list_propositions() == []

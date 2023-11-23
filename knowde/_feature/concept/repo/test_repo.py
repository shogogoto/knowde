"""repository test."""


from uuid import UUID

import pytest

from knowde._feature.concept.domain import Concept
from knowde._feature.concept.error import NotUniqueFoundError

from .repo import (
    change_concept,
    complete_concept,
    delete_concept,
    find_one,
    list_by_pref_uid,
    list_concepts,
    save_concept,
)


def test_save() -> None:
    """Create and read the created."""
    c = Concept(name="test_create")
    lc = save_concept(c)
    assert lc.uid is not None
    assert lc.created == lc.updated
    save_concept(lc)
    # assert lc2.created != lc2.updated # microsecを省いたのでズレなくなった


def test_list() -> None:
    """Find all concepts."""
    c = Concept(name="test_list")
    save_concept(c)
    ls = list_concepts()
    assert c.name in [e.name for e in ls]


def test_delete() -> None:
    """Test."""
    c = Concept(name="test_delete")
    saved = save_concept(c)
    ls = list_concepts()
    assert c.name in [e.name for e in ls]
    delete_concept(saved.valid_uid)
    ls = list_concepts()
    assert c.name not in [e.name for e in ls]


def test_change() -> None:
    """Test."""
    c = Concept(name="test_change")
    saved = save_concept(c)
    chname = "changed_name"
    change_concept(saved.valid_uid, name=chname)
    one = find_one(saved.uid)
    assert one.name == chname
    assert one.explain is None

    chexplain = "changed_explain"
    change_concept(saved.valid_uid, explain=chexplain)
    one = find_one(saved.uid)
    assert one.name == chname
    assert one.explain == chexplain


def test_list_by_pref_uid() -> None:
    """Test."""
    uid1 = UUID("ffffff75-daef-470c-a0f3-192f920797a3")
    uid2 = UUID("ffffff76-daef-470c-a0f3-192f920797a3")
    c1 = Concept(uid=uid1, name="startswith1")
    c2 = Concept(uid=uid2, name="startswith2")
    save_concept(c1)
    save_concept(c2)
    result = list_by_pref_uid("ffffff")
    assert len(result) == 2  # noqa: PLR2004
    assert {c1.name, c2.name} == {e.name for e in result}


def test_complete() -> None:
    """Test."""
    with pytest.raises(NotUniqueFoundError):
        complete_concept("ffffffffffffffffffff")
    uid = UUID("d8750567-eb54-41a1-b63d-48fbd4c8000f")
    c = Concept(uid=uid, name="complete")
    save_concept(c)
    fine_pref_uid = "d8750567"
    assert complete_concept(fine_pref_uid).valid_uid == uid

    uid = UUID("d8750567-eb54-41a1-b63d-48fbd4c8000a")
    c = Concept(uid=uid, name="complete")
    save_concept(c)
    with pytest.raises(NotUniqueFoundError):
        complete_concept(fine_pref_uid)

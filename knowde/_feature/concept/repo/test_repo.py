"""repository test."""
from uuid import UUID

import pytest

from knowde._feature.concept.domain.domain import ChangeProp, SaveProp
from knowde._feature.concept.error import CompleteMultiHitError, CompleteNotFoundError

from .label import complete_concept, list_by_pref_uid
from .repo import (
    change_concept,
    delete_concept,
    find_one,
    list_concepts,
    save_concept,
)


def test_save() -> None:
    """Create and read the created."""
    prop = SaveProp(name="test_create")
    c = save_concept(prop)
    assert c.uid is not None
    assert c.created == c.updated
    # assert lc2.created != lc2.updated # microsecを省いたのでズレなくなった


def test_list() -> None:
    """Find all concepts."""
    prop = SaveProp(name="test_list")
    save_concept(prop)
    ls = list_concepts()
    assert prop.name in [e.name for e in ls]


def test_delete() -> None:
    """Test."""
    prop = SaveProp(name="test_delete")
    saved = save_concept(prop)
    ls = list_concepts()
    assert prop.name in [e.name for e in ls]
    delete_concept(saved.valid_uid)
    ls = list_concepts()
    assert prop.name not in [e.name for e in ls]


def test_change() -> None:
    """Test."""
    prop = SaveProp(name="test_change")
    saved = save_concept(prop)
    chname = "changed_name"
    change_concept(saved.valid_uid, ChangeProp(name=chname))
    one = find_one(saved.valid_uid)
    assert one.name == chname
    assert one.explain is None

    chexplain = "changed_explain"
    change_concept(saved.valid_uid, ChangeProp(explain=chexplain))
    one = find_one(saved.valid_uid)
    assert one.name == chname
    assert one.explain == chexplain


def test_list_by_pref_uid() -> None:
    """Test."""
    uid1 = UUID("ffffff75-daef-470c-a0f3-192f920797a3")
    uid2 = UUID("ffffff76-daef-470c-a0f3-192f920797a3")
    p1 = SaveProp(uid=uid1, name="startswith1")
    p2 = SaveProp(uid=uid2, name="startswith2")
    save_concept(p1)
    save_concept(p2)
    result = list_by_pref_uid("ffffff")
    assert len(result) == 2  # noqa: PLR2004
    assert {p1.name, p2.name} == {e.name for e in result}


def test_complete() -> None:
    """Test."""
    with pytest.raises(CompleteNotFoundError):
        complete_concept("ffffffffffffffffffff")
    uid = UUID("d8750567-eb54-41a1-b63d-48fbd4c8000f")
    p = SaveProp(uid=uid, name="complete")
    save_concept(p)
    fine_pref_uid = "d8750567"
    assert complete_concept(fine_pref_uid).valid_uid == uid

    uid = UUID("d8750567-eb54-41a1-b63d-48fbd4c8000a")
    p = SaveProp(uid=uid, name="complete")
    save_concept(p)
    with pytest.raises(CompleteMultiHitError):
        complete_concept(fine_pref_uid)


def test_find_one() -> None:
    name = "m2l"
    m = save_concept(SaveProp(name=name))
    assert m.valid_uid == find_one(m.valid_uid).valid_uid

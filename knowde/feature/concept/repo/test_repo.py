"""repository test."""


from knowde.feature.concept.domain import Concept

from .repo import delete_concept, list_concepts, save_concept


def test_save() -> None:
    """Create and read the created."""
    c = Concept(name="test_create")
    lc = save_concept(c)
    assert lc.uid is not None
    assert lc.created == lc.updated
    lc2 = save_concept(lc)
    assert lc2.created != lc2.updated


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

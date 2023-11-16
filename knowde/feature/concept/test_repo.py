"""repository test."""


from knowde.feature.concept.domain import Concept
from knowde.feature.concept.repo import list_concepts, save_concept


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
    print(ls)
    assert c.name in [e.name for e in ls]

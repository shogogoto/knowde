"""repository test."""


from knowde.feature.concept.domain import Concept
from knowde.feature.concept.repo import save_concept


def test_save() -> None:
    """Create and read the created."""
    c = Concept(name="test_create")
    lc = save_concept(c)
    assert lc.uid is not None
    assert lc.created == lc.updated
    lc2 = save_concept(lc)
    assert lc2.created != lc2.updated

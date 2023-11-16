"""concept repository."""
from __future__ import annotations

from knowde.feature.concept.domain import Concept
from knowde.feature.concept.label import LConcept


def to_model(label: LConcept) -> Concept:
    """Db mapper to domain model."""
    return Concept.model_validate(label.__properties__)


def save_concept(c: Concept) -> Concept:
    """Create concept."""
    lc = LConcept(**c.model_dump()).save()
    return to_model(lc)


def list_concepts() -> list[Concept]:
    """Find all concepts."""
    ls = LConcept.nodes.all()
    return [to_model(e) for e in ls]

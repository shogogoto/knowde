"""concept repository."""
from __future__ import annotations

from knowde.feature.concept.domain import Concept
from knowde.feature.concept.label import LConcept


def save_concept(c: Concept) -> Concept:
    """Create concept."""
    lc = LConcept(**c.model_dump()).save()
    return Concept.model_validate(lc.__properties__)

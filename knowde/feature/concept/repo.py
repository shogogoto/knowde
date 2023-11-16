"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde.feature.concept.domain import Concept
from knowde.feature.concept.label import LConcept

if TYPE_CHECKING:
    from uuid import UUID


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


def delete_concept(uid: UUID) -> None:
    """Delete concept."""
    LConcept.nodes.first(uid=uid.hex).delete()

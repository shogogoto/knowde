"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from knowde.feature.concept.domain import Concept, ConceptProp
from knowde.feature.concept.error import NotOnlyMatchError

from .label import LConcept

if TYPE_CHECKING:
    from uuid import UUID


def to_model(label: LConcept) -> Concept:
    """Db mapper to domain model."""
    return Concept.model_validate(label.__properties__)


def save_concept(c: Concept | ConceptProp) -> Concept:
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


def change_concept(
    uid: UUID,
    name: str | None = None,
    explain: Optional[str] = None,
) -> Concept:
    """Change concept properties."""
    c = LConcept.nodes.first(uid=uid.hex)
    if name is not None:
        c.name = name
    if explain is not None:
        c.explain = explain
    return to_model(c.save())


def find_one(uid: UUID) -> Concept:
    """Find only one."""
    ls = LConcept.nodes.filter(uid=uid.hex)
    if len(ls) != 1:
        raise NotOnlyMatchError
    return to_model(ls[0])

"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature.concept.domain import Concept, ConceptProp
from knowde._feature.concept.error import NotUniqueFoundError

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
    explain: str | None = None,
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
    return LConcept.nodes.get(uid=uid.hex)


def list_by_pref_uid(pref_uid: str) -> list[Concept]:
    """uidの前方一致で検索."""
    return LConcept.nodes.filter(uid__startswith=pref_uid)


def complete_concept(pref_uid: str) -> Concept:
    """uuidが前方一致する要素を1つ返す."""
    ls = list_by_pref_uid(pref_uid)
    if len(ls) != 1:
        raise NotUniqueFoundError
    return to_model(ls[0])

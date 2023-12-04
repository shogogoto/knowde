"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature.concept.repo.repo_rel import find_adjacent, save_adjacent

from .label import LConcept, find_one_, to_model

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.concept.domain import Concept
    from knowde._feature.concept.domain.domain import ChangeProp, SaveProp
    from knowde._feature.concept.domain.rel import AdjacentConcept


def save_concept(p: SaveProp) -> AdjacentConcept:
    """Create concept."""
    lc = LConcept(**p.model_dump()).save()
    saved = to_model(lc)
    save_adjacent(saved.valid_uid, p)
    return find_adjacent(saved.valid_uid)


def list_concepts() -> list[Concept]:
    """Find all concepts."""
    ls = LConcept.nodes.all()
    return [to_model(e) for e in ls]


def delete_concept(uid: UUID) -> None:
    """Delete concept."""
    find_one_(uid).delete()


def change_concept(uid: UUID, p: ChangeProp) -> Concept:
    """Change concept properties."""
    c = find_one_(uid)
    if p.name is not None:
        c.name = p.name
    if p.explain is not None:
        c.explain = p.explain
    return to_model(c.save())


def find_one(uid: UUID) -> Concept:
    """Find only one."""
    return to_model(find_one_(uid))

"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature.concept.repo.repo_rel import find_adjacent, save_adjacent

from .label import util_concept

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.concept.domain import Concept
    from knowde._feature.concept.domain.domain import ChangeProp, SaveProp
    from knowde._feature.concept.domain.rel import AdjacentConcept


def save_concept(p: SaveProp) -> AdjacentConcept:
    """Create concept."""
    saved = util_concept.create(**p.model_dump())
    save_adjacent(saved.valid_uid, p)
    return find_adjacent(saved.valid_uid)


def change_concept(uid: UUID, p: ChangeProp) -> Concept:
    """Change concept properties."""
    lb = util_concept.find_one(uid)
    if p.name is not None:
        lb.name = p.name
    if p.explain is not None:
        lb.explain = p.explain
    return util_concept.to_model(lb.save())


def find_one(uid: UUID) -> Concept:
    """Find only one."""
    lb = util_concept.find_one(uid)
    return util_concept.to_model(lb)

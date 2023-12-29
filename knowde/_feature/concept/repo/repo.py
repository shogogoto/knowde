"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from knowde._feature.concept.domain import Concept
from knowde._feature.concept.repo.repo_rel import find_adjacent, save_adjacent

from .label import util_concept

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.concept.domain.domain import SaveProp
    from knowde._feature.concept.domain.rel import AdjacentConcept


def save_concept(p: SaveProp) -> AdjacentConcept:
    """Create concept."""
    saved = util_concept.create(**p.model_dump()).to_model()
    save_adjacent(saved.valid_uid, p)
    return find_adjacent(saved.valid_uid)


def change_concept(
    uid: UUID,
    name: Optional[str] = None,
    explain: Optional[str] = None,
) -> Concept:
    """Change concept properties."""
    lb = util_concept.find_one(uid).label
    if name is not None:
        lb.name = name
    if explain is not None:
        lb.explain = explain
    return Concept.to_model(lb.save())

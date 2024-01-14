"""concept api."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status
from neomodel import db

from knowde._feature._shared import set_basic_router
from knowde._feature.concept.api.util import PREFIX, TAG
from knowde._feature.concept.domain import (  # noqa: TCH001
    AdjacentConcept,
    ChangeProp,
    Concept,
    SaveProp,
)
from knowde._feature.concept.repo.label import util_concept
from knowde._feature.concept.repo.repo import (
    change_concept,
    save_concept,
)

concept_router, _ = set_basic_router(
    util_concept,
    APIRouter(prefix=PREFIX, tags=[TAG]),
)


@concept_router.post("", status_code=status.HTTP_201_CREATED)
def _post(prop: SaveProp) -> AdjacentConcept:
    """Create Concept."""
    with db.transaction:
        return save_concept(prop)


@concept_router.put(
    "/{concept_id}",
    status_code=status.HTTP_200_OK,
)
def _put(
    concept_id: UUID,
    prop: ChangeProp,
) -> Concept:
    """Change Concept."""
    return change_concept(concept_id, prop.name, prop.explain)

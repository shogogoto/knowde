"""concept api."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from fastapi import status
from neomodel import db

from knowde._feature._shared.api.crud import CRUDRouter
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

concept_router = CRUDRouter(util=util_concept).create(PREFIX, [TAG])


@concept_router.post("", status_code=status.HTTP_201_CREATED)
def _post(prop: SaveProp) -> AdjacentConcept:
    """Create Concept."""
    with db.transaction:
        return save_concept(prop)


@concept_router.put(
    "/{concept_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
def _put(
    concept_id: UUID,
    prop: ChangeProp,
) -> Concept:
    """Delete Concept."""
    return change_concept(concept_id, prop)

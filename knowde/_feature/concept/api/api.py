"""concept api."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status
from neomodel import db

from knowde._feature.concept.api.util import PREFIX, TAG
from knowde._feature.concept.domain import (  # noqa: TCH001
    AdjacentConcept,
    ChangeProp,
    Concept,
    SaveProp,
)
from knowde._feature.concept.repo.label import complete_concept
from knowde._feature.concept.repo.repo import (
    change_concept,
    delete_concept,
    list_concepts,
    save_concept,
)

concept_router = APIRouter(
    prefix=PREFIX,
    tags=[TAG],
)


@concept_router.get("")
def _get() -> list[Concept]:
    """List."""
    return list_concepts()


@concept_router.get("/completion")
def _complete(pref_uid: str) -> Concept:
    """Search concept by startswith uid."""
    return complete_concept(pref_uid)


@concept_router.post("", status_code=status.HTTP_201_CREATED)
def _post(prop: SaveProp) -> AdjacentConcept:
    """Create Concept."""
    with db.transaction:
        return save_concept(prop)


@concept_router.delete(
    "/{concept_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def _delete(concept_id: UUID) -> None:
    """Delete Concept."""
    delete_concept(concept_id)


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
    return change_concept(concept_id, **prop.model_dump())


# @concept_router.post("/{concept_id}/source", status_code==status.HTTP_201_CREATED)
# def _connect_source()

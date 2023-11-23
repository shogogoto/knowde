"""concept api."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status

from knowde._feature.concept.domain import (  # noqa: TCH001
    Concept,
    ConceptChangeProp,
    ConceptProp,
)
from knowde._feature.concept.repo.repo import (
    change_concept,
    complete_concept,
    delete_concept,
    list_concepts,
    save_concept,
)

concept_router = APIRouter(prefix="/concepts")

#### Read


@concept_router.get("")
def _get() -> list[Concept]:
    """List."""
    return list_concepts()


@concept_router.get("/completion")
def _complete(pref_uid: str) -> Concept:
    """Search concept by startswith uid."""
    return complete_concept(pref_uid)


#### Write


@concept_router.post("", status_code=status.HTTP_201_CREATED)
def _post(prop: ConceptProp) -> Concept:
    """Create Concept."""
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
    prop: ConceptChangeProp,
) -> Concept:
    """Delete Concept."""
    return change_concept(concept_id, **prop.model_dump())

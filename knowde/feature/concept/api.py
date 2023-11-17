"""concept api."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status

from knowde.feature.concept.domain import Concept, ConceptProp  # noqa: TCH001
from knowde.feature.concept.repo.repo import delete_concept, list_concepts, save_concept

concept_router = APIRouter(prefix="/concepts")


@concept_router.get("")
def _get() -> list[Concept]:
    """List."""
    return list_concepts()


@concept_router.post("", status_code=status.HTTP_201_CREATED)
def _post(c: ConceptProp) -> Concept:
    """Create Concept."""
    return save_concept(c)


@concept_router.delete(
    "/{concept_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def _delete(concept_id: UUID) -> None:
    """Delete Concept."""
    delete_concept(concept_id)

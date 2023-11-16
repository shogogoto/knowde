"""concept api."""
from __future__ import annotations

from fastapi import APIRouter, status

from knowde.feature.concept.domain import Concept, ConceptProp  # noqa: TCH001
from knowde.feature.concept.repo.repo import list_concepts, save_concept

concept_router = APIRouter(prefix="/concepts")


@concept_router.get("")
def _get() -> list[Concept]:
    """List."""
    return list_concepts()


@concept_router.post("", status_code=status.HTTP_201_CREATED)
def _post(c: ConceptProp) -> Concept:
    """Create Concept."""
    return save_concept(c)

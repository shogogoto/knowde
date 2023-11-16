"""concept api."""
from __future__ import annotations

from fastapi import APIRouter

from knowde.feature.concept.domain import Concept  # noqa: TCH001
from knowde.feature.concept.repo.repo import list_concepts

concept_router = APIRouter(prefix="/concepts")


@concept_router.get("")
def _get() -> list[Concept]:
    """List."""
    return list_concepts()

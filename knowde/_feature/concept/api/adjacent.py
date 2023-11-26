from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status
from neomodel import db

from knowde._feature.concept.api.util import PREFIX, TAG
from knowde._feature.concept.domain import (  # noqa: TCH001
    AdjacentConcept,
    AdjacentIdsProp,
    ConnectedConcept,
)
from knowde._feature.concept.repo.repo_rel import (
    disconnect_all,
    find_adjacent,
    save_adjacent,
)

concept_adj_router = APIRouter(
    prefix=f"{PREFIX}/{{concept_id}}/adjacent",
    tags=[f"{TAG}/adjacent"],
)


@concept_adj_router.get("")
def _get(concept_id: UUID) -> list[ConnectedConcept]:
    """Search concept by startswith uid."""
    return find_adjacent(concept_id).flatten()


@concept_adj_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def _delete(concept_id: UUID) -> None:
    """Delete all connections with this concept."""
    _id = concept_id


@concept_adj_router.put("")
def _put(concept_id: UUID, prop: AdjacentIdsProp) -> AdjacentConcept:
    with db.transaction:
        disconnect_all(concept_id)
        save_adjacent(concept_id, prop)
        return find_adjacent(concept_id)

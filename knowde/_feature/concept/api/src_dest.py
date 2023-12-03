from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status
from neomodel import db

from knowde._feature.concept.api.util import PREFIX, TAG
from knowde._feature.concept.domain.rel import (  # noqa: TCH001
    AdjacentConcept,
    DestinationProp,
    SourceProp,
)
from knowde._feature.concept.repo.repo_rel import disconnect
from knowde._feature.concept.repo.repo_srcdest import add_destination, add_source

concept_src_router = APIRouter(
    prefix=f"{PREFIX}/{{concept_id}}/sources",
    tags=[f"{TAG}/sources"],
)


@concept_src_router.post("")
def _create_src(concept_id: UUID, prop: SourceProp) -> AdjacentConcept:
    """Create connection from source."""
    with db.transaction:
        return add_source(concept_id, prop)


@concept_src_router.delete(
    "/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def _delete_src(concept_id: UUID, source_id: UUID) -> None:
    disconnect(source_id, concept_id)


concept_dest_router = APIRouter(
    prefix=f"{PREFIX}/{{concept_id}}/destinations",
    tags=[f"{TAG}/destinations"],
)


@concept_dest_router.post("")
def _create_dest(concept_id: UUID, prop: DestinationProp) -> AdjacentConcept:
    """Create connection from source."""
    with db.transaction:
        return add_destination(concept_id, prop)


@concept_dest_router.delete(
    "/{destination_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def _delete_dest(concept_id: UUID, destination_id: UUID) -> None:
    disconnect(concept_id, destination_id)

from uuid import UUID

from knowde._feature.concept.domain.domain import SaveProp
from knowde._feature.concept.domain.rel import (
    AdjacentConcept,
    DestinationProp,
    SourceProp,
)
from knowde._feature.concept.repo.repo import change_concept, save_concept
from knowde._feature.concept.repo.repo_rel import connect, find_adjacent


def add_source(dest_id: UUID, prop: SourceProp) -> AdjacentConcept:
    if prop.source_id is None:
        src = save_concept(SaveProp(name=prop.name, explain=prop.explain))
    else:
        src = change_concept(prop.source_id, prop)
    connect(src.valid_uid, dest_id)
    return find_adjacent(src.valid_uid)


def add_destination(src_id: UUID, prop: DestinationProp) -> AdjacentConcept:
    if prop.destination_id is None:
        dest = save_concept(SaveProp(name=prop.name, explain=prop.explain))
    else:
        dest = change_concept(prop.destination_id, prop)
    connect(src_id, dest.valid_uid)
    return find_adjacent(dest.valid_uid)

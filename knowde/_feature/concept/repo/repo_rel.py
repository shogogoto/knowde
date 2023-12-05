"""concept repository for relationship."""

from uuid import UUID

from knowde._feature.concept.domain import AdjacentConcept
from knowde._feature.concept.domain.domain import AdjacentIdsProp
from knowde._feature.concept.error import ConnectionNotFoundError
from knowde._feature.concept.repo.label import (
    LConcept,
    complete_concept,
    util_concept,
)


def find_adjacent(concept_uid: UUID) -> AdjacentConcept:
    """List connected concepts."""
    lc: LConcept = util_concept.find_one(concept_uid)
    return AdjacentConcept(
        **util_concept.to_model(lc).model_dump(),
        srcs=[util_concept.to_model(e) for e in lc.src.all()],
        dests=[util_concept.to_model(e) for e in lc.dest.all()],
    )


def connect(from_uid: UUID, to_uid: UUID) -> None:
    """Connect two concepts."""
    cfrom: LConcept = util_concept.find_one(from_uid)
    cto: LConcept = util_concept.find_one(to_uid)
    cfrom.dest.connect(cto)


def disconnect(from_uid: UUID, to_uid: UUID) -> None:
    """Discommenct two concepts."""
    cfrom: LConcept = util_concept.find_one(from_uid)
    cto = cfrom.dest.get_or_none(uid=to_uid.hex)
    if cto is None:
        msg = f"({from_uid})->({to_uid})は繋がっていなかった"
        raise ConnectionNotFoundError(msg)
    cfrom.dest.disconnect(cto)


def disconnect_all(concept_uid: UUID) -> None:
    lc: LConcept = util_concept.find_one(concept_uid)
    lc.src.disconnect_all()
    lc.dest.disconnect_all()


def disconnect_srcs(concept_uid: UUID) -> None:
    lc: LConcept = util_concept.find_one(concept_uid)
    lc.src.disconnect_all()


def disconnect_dests(concept_uid: UUID) -> None:
    lc: LConcept = util_concept.find_one(concept_uid)
    lc.dest.disconnect_all()


def save_adjacent(center_id: UUID, prop: AdjacentIdsProp) -> None:
    for sid in prop.src_ids:
        src = complete_concept(sid)
        connect(src.valid_uid, center_id)
    for did in prop.dest_ids:
        dest = complete_concept(did)
        connect(center_id, dest.valid_uid)

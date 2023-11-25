"""concept repository for relationship."""

from uuid import UUID

from knowde._feature.concept.domain import AdjacentConcept
from knowde._feature.concept.repo.label import LConcept
from knowde._feature.concept.repo.repo import to_model


def find_adjacent(concept_uid: UUID) -> AdjacentConcept:
    """List connected concepts."""
    lc: LConcept = LConcept.nodes.get(uid=concept_uid.hex)
    return AdjacentConcept(
        **to_model(lc).model_dump(),
        sources=[to_model(e) for e in lc.src.all()],
        dests=[to_model(e) for e in lc.dest.all()],
    )


def connect(from_uid: UUID, to_uid: UUID) -> bool:
    """Connect two concepts."""
    cfrom: LConcept = LConcept.nodes.get(uid=from_uid.hex)
    cto: LConcept = LConcept.nodes.get(uid=to_uid.hex)
    return cfrom.dest.connect(cto)


def disconnect(from_uid: UUID, to_uid: UUID) -> bool:
    """Discommenct two concepts."""
    cfrom: LConcept = LConcept.nodes.get(uid=from_uid.hex)
    cto = cfrom.dest.get_or_none(uid=to_uid.hex)
    if cto is None:
        # そもそも繋がっていなかった
        return False
    cfrom.dest.disconnect(cto)
    # 無事disconnectされてdestが取得できなくなった
    return cfrom.dest.get_or_none(uid=to_uid.hex) is None

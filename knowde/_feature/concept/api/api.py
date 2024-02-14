"""concept api."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from neomodel import db

from knowde._feature._shared import set_basic_router
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import (  # noqa: TCH001
    AdjacentConcept,
    ChangeProp,
    Concept,
    SaveProp,
)
from knowde._feature.concept.repo.label import util_concept
from knowde._feature.concept.repo.repo import (
    change_concept,
    save_concept,
)

concept_router, reqs, _ = set_basic_router(
    util_concept,
    Endpoint.Concept.create_router(),
)


def _post(prop: SaveProp) -> AdjacentConcept:
    """Create Concept."""
    with db.transaction:
        return save_concept(prop)


reqs.post(_post)


def _put(
    concept_id: UUID,
    prop: ChangeProp,
) -> Concept:
    """Change Concept."""
    return change_concept(concept_id, prop.name, prop.explain)


reqs.put(_put)

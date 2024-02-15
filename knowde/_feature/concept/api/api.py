"""concept api."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from neomodel import db

from knowde._feature._shared.api.client_factory import create_basic_clients
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature._shared.integrated_interface.generate_req import APIRequests
from knowde._feature.concept.domain import (  # noqa: TCH001
    AdjacentConcept,
    ChangeProp,
    Concept,
    SaveProp,
)
from knowde._feature.concept.repo.repo import (
    change_concept,
    save_concept,
    util_concept,
)

concept_router = Endpoint.Concept.create_router()
_ = create_basic_clients(util_concept, concept_router)
reqs = APIRequests(router=concept_router)


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

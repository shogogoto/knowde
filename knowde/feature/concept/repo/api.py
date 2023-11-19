"""for api."""
from __future__ import annotations

from knowde.feature._shared.endpoint import Endpoint
from knowde.feature.concept.domain import Concept


def req_list_concepts() -> list[Concept]:
    """Request list concepts."""
    res = Endpoint.Concept.get()
    return [Concept.model_validate(e) for e in res.json()]

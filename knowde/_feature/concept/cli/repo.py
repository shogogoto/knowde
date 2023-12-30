"""api repository for cli."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.cli.request import CliRequest
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import ChangeProp, Concept, ConceptProp

if TYPE_CHECKING:
    from uuid import UUID

req_concept = CliRequest(
    endpoint=Endpoint.Concept,
    M=Concept,
)


def req_add(p: ConceptProp) -> Concept:
    """Request create concept."""
    res = Endpoint.Concept.post(json=p.model_dump())
    return Concept.model_validate(res.json())


def req_change(uid: UUID, prop: ChangeProp) -> Concept:
    """Request change concept."""
    res = Endpoint.Concept.put(uid.hex, json=prop.model_dump())
    return Concept.model_validate(res.json())

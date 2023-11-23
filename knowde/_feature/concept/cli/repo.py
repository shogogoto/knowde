"""api repository for cli."""
from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.status import HTTP_204_NO_CONTENT

from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import Concept, ConceptChangeProp, ConceptProp

if TYPE_CHECKING:
    from uuid import UUID


def req_list() -> list[Concept]:
    """Request list concepts."""
    res = Endpoint.Concept.get()
    return [Concept.model_validate(e) for e in res.json()]


def req_add(c: ConceptProp) -> Concept:
    """Request create concept."""
    res = Endpoint.Concept.post(json=c.model_dump())
    return Concept.model_validate(res.json())


def req_remove(uid: UUID) -> None:
    """Request delete concept."""
    res = Endpoint.Concept.delete(uid.hex)
    if res.status_code != HTTP_204_NO_CONTENT:
        pass


def req_change(uid: UUID, prop: ConceptChangeProp) -> Concept:
    """Request change concept."""
    res = Endpoint.Concept.put(uid.hex, json=prop.model_dump())
    return Concept.model_validate(res.json())


def req_complete(pref_uid: str) -> Concept:
    """Request concept by startswith uid."""
    res = Endpoint.Concept.get(f"completion?pref_uid={pref_uid}")
    return Concept.model_validate(res.json())

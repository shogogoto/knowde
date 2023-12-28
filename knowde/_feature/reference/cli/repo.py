"""apiに依存."""
from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.status import HTTP_204_NO_CONTENT

from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.reference.domain.domain import Reference

if TYPE_CHECKING:
    from uuid import UUID


def req_list() -> list[Reference]:
    res = Endpoint.Reference.get()
    return [Reference.model_validate(e) for e in res.json()]


def req_add(name: str) -> Reference:
    res = Endpoint.Reference.post(
        json={
            "name": name,
        },
    )
    return Reference.model_validate(res.json())


def req_rm(uid: UUID) -> None:
    res = Endpoint.Reference.delete(uid.hex)
    if res.status_code != HTTP_204_NO_CONTENT:
        pass

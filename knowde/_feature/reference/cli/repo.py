"""apiに依存."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.cli.request import CliRequest
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.reference.domain.domain import Reference

if TYPE_CHECKING:
    from uuid import UUID


ref_req = CliRequest(
    endpoint=Endpoint.Reference,
    M=Reference,
)


def req_add(name: str) -> Reference:
    res = Endpoint.Reference.post(
        json={
            "name": name,
        },
    )
    return Reference.model_validate(res.json())


def req_change_name(uid: UUID, name: str) -> Reference:
    res = Endpoint.Reference.put(uid.hex, json={"name": name})
    return Reference.model_validate(res.json())

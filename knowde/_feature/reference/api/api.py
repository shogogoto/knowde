from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from knowde._feature._shared import Endpoint
from knowde._feature._shared.api.client_factory import create_basic_clients
from knowde._feature.reference.api.param import (  # noqa: TCH001
    NameParam,
    SubReferenceParam,
)
from knowde._feature.reference.domain.domain import Reference  # noqa: TCH001
from knowde._feature.reference.repo.node import (
    add_part,
    add_root,
    change_name,
    ref_util,
)

ref_router = Endpoint.Reference.create_router()

_ = create_basic_clients(ref_util, ref_router)


@ref_router.post("")
def add_ref(p: NameParam) -> Reference:
    return add_root(p.name)


@ref_router.put("/{ref_id}")
def _put(ref_id: UUID, p: NameParam) -> Reference:
    return change_name(ref_id, p.name)


@ref_router.post("/{ref_id}")
def add_subref(p: SubReferenceParam) -> Reference:
    return add_part(p.ref_id, p.name)

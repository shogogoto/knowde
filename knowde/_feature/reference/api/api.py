from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from knowde._feature._shared.api.crud import CRUDRouter
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.reference.api.param import (  # noqa: TCH001
    NameParam,
    SubReferenceParam,
)
from knowde._feature.reference.domain.domain import Reference  # noqa: TCH001
from knowde._feature.reference.repo.label import ref_util
from knowde._feature.reference.repo.node import (
    add_part,
    add_root,
    change_name,
    find_roots,
)

_EP = Endpoint.Reference


ref_router = CRUDRouter(
    util=ref_util,
    ls_all=lambda: find_roots().roots,
).create(
    f"/{_EP.value}",
    [f"{_EP.single_form}"],
)


@ref_router.post("")
def add_ref(p: NameParam) -> Reference:
    return add_root(p.name)


@ref_router.put("/{ref_id}")
def _put(ref_id: UUID, p: NameParam) -> Reference:
    return change_name(ref_id, p.name)


@ref_router.post("/{ref_id}")
def add_subref(p: SubReferenceParam) -> Reference:
    return add_part(p.ref_id, p.name)

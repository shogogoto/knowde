from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from uuid import UUID

from fastapi import APIRouter  # noqa: TCH002
from pydantic import BaseModel
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.api.client import (
    add_client,
    change_client,
    complete_client,
    list_client,
    remove_client,
)
from knowde._feature._shared.api.endpoint_funcs import EndpointFuncs
from knowde._feature._shared.api.types import (
    Add,
    BasicClients,
    Change,
    CheckResponse,
    Complete,
    ListClient,
    Remove,
)
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

from .generate_req import (
    APIRequests,
    inject_signature,
)

if TYPE_CHECKING:
    from knowde._feature._shared.domain import DomainModel


def create_add_client(
    router: APIRouter,
    f: Callable,
    t_in: type[BaseModel],
    t_out: type[DomainModel],
    check_response: CheckResponse | None = None,
) -> Add:
    reqs = APIRequests(router=router)
    req_add = reqs.post(
        inject_signature(f, [t_in], t_out),
    )
    return add_client(req_add, t_in, t_out, check_response)


def create_change_client(
    router: APIRouter,
    f: Callable,
    t_in: type[BaseModel],
    t_out: type[DomainModel],
    complete_client: Complete,
) -> Change:
    reqs = APIRequests(router=router)
    OPT = create_partial_model(t_in)  # noqa: N806
    req_ch = reqs.put(
        inject_signature(f, [UUID, OPT], t_out),
    )
    return change_client(req_ch, OPT, t_out, complete_client)


def create_complete_client(
    router: APIRouter,
    f: Complete,
    t_out: type[DomainModel],
) -> Complete:
    reqs = APIRequests(router=router)
    req_complete = reqs.get(
        inject_signature(f, [str], t_out),
        "/completion",
    )
    return complete_client(req_complete, t_out)


def create_remove_client(
    router: APIRouter,
    f: Remove,
) -> Remove:
    reqs = APIRequests(router=router)
    req_rm = reqs.delete(inject_signature(f, [UUID]))
    return remove_client(req_rm)


def create_list_client(
    router: APIRouter,
    f: Callable,
    t_out: type[DomainModel],
    t_in: type[BaseModel] | None = None,
    check_response: CheckResponse | None = None,
) -> ListClient:
    reqs = APIRequests(router=router)
    if t_in is None:
        f_di = inject_signature(f, [], list[t_out])
    else:
        f_di = inject_signature(f, [t_in], list[t_out])
    req_ls = reqs.get(f_di)
    return list_client(req_ls, t_out, t_in, check_response)


def create_basic_clients(
    util: LabelUtil,
    router: APIRouter,
) -> BasicClients:
    """labelに対応したCRUD APIの基本的な定義."""
    epfs = EndpointFuncs(util=util)
    return BasicClients(
        create_remove_client(router, epfs.rm),
        create_complete_client(router, epfs.complete, util.model),
        create_list_client(router, epfs.ls, util.model),
    )


class APIClientFactory(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    util: LabelUtil
    router: APIRouter

    @property
    def t_out(self) -> type[DomainModel]:
        return self.util.model

    def create_basics(self) -> BasicClients:
        return create_basic_clients(
            self.util,
            self.router,
        )

    def create_add(
        self,
        t_in: type[BaseModel],
    ) -> Add:
        epfs = EndpointFuncs(util=self.util)
        return create_add_client(
            self.router,
            epfs.add_factory(t_in),
            t_in,
            self.util.model,
        )

    def create_change(
        self,
        t_in: type[BaseModel],
    ) -> Change:
        epfs = EndpointFuncs(util=self.util)
        f = epfs.ch_factory(t_in)
        return create_change_client(
            self.router,
            f,
            t_in,
            self.util.model,
            self.create_basics().complete,
        )

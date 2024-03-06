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


def create_basic_clients(
    util: LabelUtil,
    router: APIRouter,
) -> BasicClients:
    """labelに対応したCRUD APIの基本的な定義."""
    reqs = APIRequests(router=router)
    epfs = EndpointFuncs(util=util)

    req_rm = reqs.delete(inject_signature(epfs.rm, [UUID]))
    req_complete = reqs.get(
        inject_signature(epfs.complete, [str], util.model),
        "/completion",
    )
    req_ls = reqs.get(inject_signature(epfs.ls, [], list[util.model]))
    return BasicClients(
        remove_client(req_rm),
        complete_client(req_complete, util.model),
        list_client(req_ls, util.model),
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

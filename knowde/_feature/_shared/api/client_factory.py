from __future__ import annotations

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
    Complete,
)
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

from .generate_req import (
    APIRequests,
    inject_signature,
)


def create_add_client(
    util: LabelUtil,
    router: APIRouter,
    t_in: type[BaseModel],
) -> Add:
    reqs = APIRequests(router=router)
    epfs = EndpointFuncs(util=util)

    req_add = reqs.post(
        inject_signature(epfs.add_factory(t_in), [t_in], util.model),
    )
    return add_client(req_add, t_in, util.model)


def create_change_client(
    util: LabelUtil,
    router: APIRouter,
    t_in: type[BaseModel],
    complete_client: Complete,
) -> Change:
    reqs = APIRequests(router=router)
    epfs = EndpointFuncs(util=util)

    OPT = create_partial_model(t_in)  # noqa: N806
    req_ch = reqs.put(
        inject_signature(epfs.ch_factory(t_in), [UUID, OPT], util.model),
    )
    return change_client(req_ch, OPT, util.model, complete_client)


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

    def create_basics(self) -> BasicClients:
        return create_basic_clients(
            self.util,
            self.router,
        )

    def create_add(
        self,
        t_in: type[BaseModel],
    ) -> Add:
        return create_add_client(
            self.util,
            self.router,
            t_in,
        )

    def create_change(
        self,
        t_in: type[BaseModel],
    ) -> Change:
        return create_change_client(
            self.util,
            self.router,
            t_in,
            self.create_basics().complete,
        )

from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from uuid import UUID

from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.api.client import (
    add_client,
    change_client,
    complete_client,
    list_client,
    remove_client,
)
from knowde._feature._shared.api.endpoint_funcs import EndpointFuncs
from knowde._feature._shared.api.types import BasicClients, Complete
from knowde._feature._shared.integrated_interface.generate_req import (
    APIRequests,
    inject_signature,
)
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

if TYPE_CHECKING:
    from fastapi import APIRouter
    from pydantic import BaseModel


def create_add_client_factory(
    util: LabelUtil,
    router: APIRouter,
) -> Callable[[type[BaseModel]], Callable]:
    reqs = APIRequests(router=router)
    epfs = EndpointFuncs(util=util)

    def _add(
        t_in: type[BaseModel],
    ) -> Callable:
        req_add = reqs.post(
            inject_signature(epfs.add_factory(t_in), [t_in], util.model),
        )
        return add_client(req_add, t_in, util.model)

    return _add


def create_change_client_factory(
    util: LabelUtil,
    router: APIRouter,
    complete_client: Complete,
) -> Callable[[type[BaseModel]], Callable]:
    reqs = APIRequests(router=router)
    epfs = EndpointFuncs(util=util)

    def _ch(
        t_in: type[BaseModel],
    ) -> Callable:
        OPT = create_partial_model(t_in)  # noqa: N806
        req_ch = reqs.put(
            inject_signature(epfs.ch_factory(t_in), [UUID, OPT], util.model),
        )
        return change_client(req_ch, OPT, util.model, complete_client)

    return _ch


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

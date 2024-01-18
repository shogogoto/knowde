"""API定義からCLI Requestを生成する."""
from __future__ import annotations

import functools
from typing import (
    TYPE_CHECKING,
    Callable,
)

from knowde._feature._shared.endpoint import Endpoint

from .flatten_param_func import change_signature

if TYPE_CHECKING:
    from fastapi import APIRouter
    from pydantic import BaseModel
    from requests import Response

    from knowde._feature._shared.integrated_interface.types import RequestGenerator

    from .types import (
        CheckResponse,
        ModelEncoder,
    )


def create_get_generator(
    router: APIRouter,
    t_in: type[BaseModel] | None,
    t_out: type,  # undefined annotation回避のために必要
    func: Callable,
    relative: str = "",
) -> tuple[
    APIRouter,
    RequestGenerator,
]:
    deco = change_signature(t_in, t_out)
    f = deco(func)
    router.get(relative)(f)
    ep = Endpoint.of(router.prefix)
    applied = functools.partial(ep.get, relative=relative)

    def _generator(
        encoder: ModelEncoder,
        check: CheckResponse | None = None,
    ) -> t_out:
        def _proc(res: Response) -> t_out:
            if check is not None:
                check(res)
            return encoder(res.json())

        if t_in is None:
            return deco(
                functools.partial(_proc, res=applied()),
            )

        @deco
        def _req_with(p: t_in) -> Response:
            res = applied(params=p.model_dump())
            return _proc(res)

        return _req_with

    return (
        router,
        _generator,
    )

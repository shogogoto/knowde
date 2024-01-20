"""API定義からCLI Requestを生成する."""
from __future__ import annotations

import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
)

from knowde._feature._shared.endpoint import Endpoint
from knowde._feature._shared.integrated_interface.types import (
    MethodType,
)

from .signaturetools import change_signature

if TYPE_CHECKING:
    from fastapi import APIRouter
    from pydantic import BaseModel
    from requests import Response

    from .types import (
        ApiMethod,
        CheckResponse,
        ModelEncoder,
        RequestGenerator,
        RequestMethod,
        Responsable,
    )


def get_pair_methods(
    router: APIRouter,
    mt: MethodType,
) -> tuple[
    ApiMethod,
    RequestMethod,
]:
    api: ApiMethod = getattr(router, mt.value)
    ep = Endpoint.of(router.prefix)
    req = getattr(ep, mt.value)
    return (api, req)


def partial_request(
    req: RequestMethod,
    mt: MethodType,
    relative: str,
    args: dict[str, Any] | None = None,
) -> Responsable:
    if mt == MethodType.GET:
        return functools.partial(
            req,
            relative=relative,
            params=args,
        )
    return functools.partial(
        req,
        relative=relative,
        json=args,
    )


def create_get_generator(  # noqa: PLR0913
    router: APIRouter,
    t_in: type[BaseModel] | None,
    t_out: type,  # undefined annotation回避のために必要
    func: Callable,
    relative: str = "",
    mt: MethodType = MethodType.GET,
) -> tuple[
    APIRouter,
    RequestGenerator,
]:
    deco = change_signature(t_in, t_out)
    f = deco(func)
    api, req = get_pair_methods(router, mt)
    api(relative)(f)

    def _generator(
        encoder: ModelEncoder,
        check: CheckResponse | None = None,
    ) -> t_out:
        def _post_response(res: Response) -> t_out:
            if check is not None:
                check(res)
            return encoder(res.json())

        if t_in is None:
            preq = partial_request(req, mt=mt, relative=relative)
            return deco(
                functools.partial(_post_response, res=preq()),
            )

        @deco
        def _req_with(p: t_in) -> Response:
            preq = partial_request(
                req,
                mt=mt,
                relative=relative,
                args=p.model_dump(),
            )
            return _post_response(preq())

        return _req_with

    return (
        router,
        _generator,
    )

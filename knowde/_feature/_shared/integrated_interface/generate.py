"""API定義からCLI Requestを生成する."""
from __future__ import annotations

import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
)

from fastapi import status

from knowde._feature._shared.endpoint import Endpoint
from knowde._feature._shared.integrated_interface.types import (
    HttpType,
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
    ht: HttpType,
) -> tuple[
    ApiMethod,
    RequestMethod,
]:
    api: ApiMethod = getattr(router, ht.value)
    ep = Endpoint.of(router.prefix)
    req = getattr(ep, ht.value)
    return (api, req)


def partial_request(
    req: RequestMethod,
    ht: HttpType,
    relative: str,
    args: dict[str, Any] | None = None,
) -> Responsable:
    if ht.is_get():
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


def create_request_generator(  # noqa: PLR0913
    router: APIRouter,
    t_in: type[BaseModel] | None,
    t_out: type,  # undefined annotation回避のために必要
    api_impl: Callable,
    relative: str = "",
    ht: HttpType = HttpType.GET,
) -> tuple[
    APIRouter,
    RequestGenerator,
]:
    deco = change_signature(t_in, t_out, only_eval=not ht.is_get())
    f = deco(api_impl)
    api, req = get_pair_methods(router, ht)
    if ht == HttpType.POST:
        api(relative, status_code=status.HTTP_201_CREATED)(f)
    if ht == HttpType.DELETE:
        api(relative, status_code=status.HTTP_204_NO_CONTENT)(f)
    else:
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
            preq = partial_request(req, ht=ht, relative=relative)
            return deco(
                functools.partial(_post_response, res=preq()),
            )

        @deco
        def _req_with(p: t_in) -> Response:
            preq = partial_request(
                req,
                ht=ht,
                relative=relative,
                args=p.model_dump(),
            )
            return _post_response(preq())

        return _req_with

    return (
        router,
        _generator,
    )

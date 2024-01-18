"""API定義からCLI Requestを生成する."""
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Protocol,
    TypeAlias,
)

from pydantic import BaseModel, JsonValue
from requests import Response

from knowde._feature._shared.endpoint import Endpoint

from .flatten_param_func import flatten_param_func

if TYPE_CHECKING:
    from fastapi import APIRouter


CheckResponse: TypeAlias = Callable[[Response], None]
ModelEncoder: TypeAlias = Callable[[JsonValue], BaseModel]


class GeneratedRequest(Protocol):
    def __call__(
        self,
        check: CheckResponse | None = None,
        # encoder: Callable[[JsonValue], T],
        encoder: ModelEncoder | None = None,
    ) -> BaseModel:
        ...


def create_get_generator(
    router: APIRouter,
    t_in: type[BaseModel],
    t_out: type[BaseModel],  # undefined annotation回避のために必要
    func: Callable,
    relative: str = "",
) -> tuple[
    APIRouter,
    Callable[..., GeneratedRequest],
]:
    f = flatten_param_func(t_in, t_out, func)
    router.get(relative)(f)
    ep = Endpoint.of(router.prefix)

    def req(p: t_in) -> Response:
        def _req(
            check: CheckResponse | None = None,
            encoder: ModelEncoder | None = None,
        ) -> t_out:
            res = ep.get(
                relative=relative,
                params=p.model_dump(),
            )
            if check is not None:
                check(res)
            if encoder is None:
                return t_out.model_validate(res.json())
            return encoder(res.json())

        return _req

    return (
        router,
        flatten_param_func(t_in, t_out, req),
    )

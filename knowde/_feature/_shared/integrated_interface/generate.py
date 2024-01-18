"""API定義からCLI Requestを生成する."""
from __future__ import annotations

from inspect import Signature
from typing import (
    TYPE_CHECKING,
    Callable,
    Protocol,
    TypeAlias,
    TypeVar,
)

from makefun import create_function
from pydantic import BaseModel, JsonValue
from requests import Response

from knowde._feature._shared.endpoint import Endpoint

from .flatten_param_func import flatten_param_func

if TYPE_CHECKING:
    from fastapi import APIRouter


a = 1

Model = TypeVar("Model", bound=BaseModel)
CheckResponse: TypeAlias = Callable[[Response], None]
ModelEncoder: TypeAlias = Callable[[JsonValue], Model]


class GeneratedRequest(Protocol):
    def __call__(
        self,
        encoder: ModelEncoder,
        check: CheckResponse | None = None,
    ) -> BaseModel:
        ...


def change_signature(  # noqa: ANN202
    t_in: type[BaseModel] | None,
    # ↓ undefined annotation回避のために必要
    t_out: type[BaseModel],
    func: Callable,
):
    if t_in is not None:
        f = flatten_param_func(t_in, t_out, func)
    else:
        f = create_function(
            Signature(return_annotation=t_out),
            func,
        )
    return f


def create_get_generator(
    router: APIRouter,
    t_in: type[BaseModel] | None,
    # ↓ undefined annotation回避のために必要
    t_out: type[BaseModel],
    func: Callable,
    relative: str = "",
) -> tuple[
    APIRouter,
    Callable[..., GeneratedRequest],
]:
    f = change_signature(t_in, t_out, func)
    router.get(relative)(f)
    ep = Endpoint.of(router.prefix)

    def _generate_req(res: Response) -> GeneratedRequest:
        def _req(
            encoder: ModelEncoder,
            check: CheckResponse | None = None,
        ) -> t_out:
            if check is not None:
                check(res)
            return encoder(res.json())

        return _req

    _req: Callable[..., GeneratedRequest]
    if t_in is None:

        def req1() -> GeneratedRequest:
            res = ep.get(relative=relative)
            return _generate_req(res)

        _req = req1
    else:

        def req2(p: t_in) -> GeneratedRequest:
            res = ep.get(
                relative=relative,
                params=p.model_dump() if p is not None else None,
            )
            return _generate_req(res)

        _req = req2

    return (
        router,
        change_signature(t_in, t_out, _req),
    )

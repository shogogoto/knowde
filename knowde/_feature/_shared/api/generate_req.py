from __future__ import annotations

from inspect import Signature, signature
from typing import TYPE_CHECKING, Callable

from fastapi import APIRouter, status
from makefun import create_function
from pydantic import BaseModel

from .endpoint import Endpoint

if TYPE_CHECKING:
    from .types import RequestMethod


def inject_signature(
    f: Callable,
    t_in: list[type],
    t_out: type | None = None,
) -> Callable:
    """API定義時に型情報が喪失する場合があるので、それを補う."""
    params = signature(f).parameters.values()
    replaced = []
    for p, t in zip(params, t_in, strict=True):
        p_new = p.replace(annotation=t)
        replaced.append(p_new)
    return create_function(
        Signature(replaced, return_annotation=t_out),
        f,
    )


class APIRequests(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    router: APIRouter

    @property
    def endpoint(self) -> Endpoint:
        return Endpoint.of(self.router.prefix)

    def post(
        self,
        f: Callable,
        path: str = "",
    ) -> RequestMethod:
        self.router.post(
            path,
            status_code=status.HTTP_201_CREATED,
        )(f)
        return self.endpoint.post

    def put(
        self,
        f: Callable,
        path: str = "/{uid}",
    ) -> RequestMethod:
        self.router.put(path)(f)
        return self.endpoint.put

    def get(
        self,
        f: Callable,
        path: str = "",
    ) -> RequestMethod:
        self.router.get(path)(f)
        return self.endpoint.get

    def delete(
        self,
        f: Callable,
        path: str = "/{uid}",
    ) -> RequestMethod:
        self.router.delete(
            path,
            status_code=status.HTTP_204_NO_CONTENT,
        )(f)
        return self.endpoint.delete

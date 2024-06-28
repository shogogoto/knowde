from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from fastapi import APIRouter, status
from pydantic import BaseModel

from knowde._feature._shared.api.endpoint import Endpoint

if TYPE_CHECKING:
    from .types import EndpointMethod


class StatusCodeGrant(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    """APIRouterにステータスコードを付与しrouterからendpointメソッドへ変換."""

    router: APIRouter

    @property
    def endpoint(self) -> Endpoint:
        return Endpoint.of(self.router.prefix)

    def to_post(
        self,
        f: Callable,
        path: str = "",
    ) -> EndpointMethod:
        self.router.post(
            path,
            status_code=status.HTTP_201_CREATED,
        )(f)
        return self.endpoint.post

    def to_put(
        self,
        f: Callable,
        path: str = "/{uid}",
    ) -> EndpointMethod:
        self.router.put(path)(f)
        return self.endpoint.put

    def to_get(
        self,
        f: Callable,
        path: str = "",
    ) -> EndpointMethod:
        self.router.get(path)(f)
        return self.endpoint.get

    def to_delete(
        self,
        f: Callable,
        path: str = "/{uid}",
    ) -> EndpointMethod:
        self.router.delete(
            path,
            status_code=status.HTTP_204_NO_CONTENT,
            response_model=None,
        )(f)
        return self.endpoint.delete

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Protocol,
    TypeAlias,
    TypeVar,
)

from requests import Response

if TYPE_CHECKING:
    import requests
    from fastapi import APIRouter


CheckResponse: TypeAlias = Callable[[Response], None]
T = TypeVar("T")


class EndpointMethod(Protocol):
    def __call__(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        ...


class ToEndpointMethod(Protocol):
    def __call__(
        self,
        f: Callable[..., T],
        path: str,
    ) -> EndpointMethod:
        ...


class Router2EndpointMethod(Protocol):
    def __call__(
        self,
        router: APIRouter,
        f: Callable,
        path: str,
    ) -> EndpointMethod:
        ...

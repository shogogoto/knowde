"""API interface type."""
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

ClientRequest: TypeAlias = Callable[..., Response]
CheckResponse: TypeAlias = Callable[[Response], None]
T = TypeVar("T")


class EndpointMethod(Protocol):
    """APIエンドポイントを叩くリクエスト."""

    def __call__(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Request."""
        ...


class ToEndpointMethod(Protocol):
    """関数 -> API Request."""

    def __call__(  # noqa: D102
        self,
        f: Callable[..., T],
        path: str,
    ) -> EndpointMethod:
        ...


class Router2EndpointMethod(Protocol):
    """fastapi router -> API Request."""

    def __call__(  # noqa: D102
        self,
        router: APIRouter,
        f: Callable,
        path: str,
    ) -> EndpointMethod:
        ...

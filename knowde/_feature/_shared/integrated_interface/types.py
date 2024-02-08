"""ロジックレスな型情報."""
from __future__ import annotations

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Protocol,
    TypeAlias,
    TypeVar,
)

from pydantic import BaseModel, Field, JsonValue
from requests import Response

if TYPE_CHECKING:
    from fastapi.types import DecoratedCallable

Model = TypeVar("Model", bound=BaseModel)
CheckResponse: TypeAlias = Callable[[Response], None]
ModelEncoder: TypeAlias = Callable[[JsonValue], Model]
Responsable: TypeAlias = Callable[[], Response]


class CompleteParam(BaseModel):
    pref_uid: str = Field(
        min_length=1,
        description="uuidと前方一致で検索",
    )


class RequestGenerator(Protocol):
    def __call__(
        self,
        encoder: ModelEncoder,
        check: CheckResponse | None = None,
    ) -> Callable[..., BaseModel]:
        ...


class ApiMethod(Protocol):
    """よく使うparamだけで十分."""

    def __call__(  # noqa: PLR0913
        self,
        path: str,
        *,
        response_model: Any = None,  # noqa: ANN401
        status_code: int | None = None,
        tags: list[str | Enum] | None = None,
        description: str | None = None,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        ...


class RequestMethod(Protocol):
    def __call__(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> Response:
        ...


class EndpointMethod(Protocol):
    def __call__(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> Response:
        ...


class HttpType(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"

    def is_get(self) -> bool:
        return self.value == "get"

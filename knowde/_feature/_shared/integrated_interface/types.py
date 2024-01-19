from __future__ import annotations

from typing import (
    Callable,
    Protocol,
    TypeAlias,
    TypeVar,
)

from pydantic import BaseModel, JsonValue
from requests import Response

Model = TypeVar("Model", bound=BaseModel)
CheckResponse: TypeAlias = Callable[[Response], None]
ModelEncoder: TypeAlias = Callable[[JsonValue], Model]


class CompleteParam(BaseModel):
    pref_uid: str


class GeneratedRequest(Protocol):
    def __call__(
        self,
        encoder: ModelEncoder,
        check: CheckResponse | None = None,
    ) -> BaseModel:
        ...


class RequestGenerator(Protocol):
    def __call__(
        self,
        encoder: ModelEncoder,
        check: CheckResponse | None = None,
    ) -> Callable[..., BaseModel]:
        ...

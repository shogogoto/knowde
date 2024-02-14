from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple, Protocol

if TYPE_CHECKING:
    from uuid import UUID

    from fastapi import APIRouter
    from pydantic import BaseModel

    from knowde._feature._shared.integrated_interface.generate_req import APIRequests


class Remove(Protocol):
    def __call__(self, uid: UUID) -> None:
        ...


class Complete(Protocol):
    def __call__(self, pref_uid: str) -> BaseModel:
        ...


class List(Protocol):
    def __call__(self) -> list[BaseModel]:
        ...


class Add(Protocol):
    def __call__(self, p: BaseModel) -> BaseModel:
        ...


class Change(Protocol):
    def __call__(
        self,
        uid: UUID,
        # PydanticPartialに合う型が分からなかった
        p: Any,  # noqa: ANN401
    ) -> BaseModel:
        ...


class BasicMethods(NamedTuple):
    rm: Remove
    complete: Complete
    ls: List


class APISetter(Protocol):
    def __call__(self, t_in: type[BaseModel]) -> None:
        ...


class ReturnType(NamedTuple):
    router: APIRouter
    requests: APIRequests
    add_and_change: APISetter

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, NamedTuple, Protocol

if TYPE_CHECKING:
    from uuid import UUID

    import requests
    from pydantic import BaseModel

    from knowde._feature._shared.domain import DomainModel


class Remove(Protocol):
    def __call__(self, uid: UUID) -> None:
        ...


class Complete(Protocol):
    def __call__(self, pref_uid: str) -> DomainModel:
        ...


class ListMethod(Protocol):
    """typing.Listと区別できる名前にした."""

    def __call__(self) -> list[DomainModel]:
        ...


class Add(Protocol):
    def __call__(self, p: BaseModel) -> DomainModel:
        ...


class Change(Protocol):
    def __call__(
        self,
        uid: UUID,
        # PydanticPartialに合う型が分からなかった
        p: Any,  # noqa: ANN401
    ) -> DomainModel:
        ...


class BasicClients(NamedTuple):
    rm: Remove
    complete: Complete
    ls: ListMethod


class AddChangeFactory(Protocol):
    def __call__(self, t_in: type[BaseModel]) -> tuple[Callable, Callable]:
        ...


class ReturnType(NamedTuple):
    add_and_change: AddChangeFactory
    methods: BasicClients


class RequestMethod(Protocol):
    def __call__(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        ...

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, RootModel

from .domain import Entity

M = TypeVar("M", bound=Entity)


class ModelList(RootModel[list[M]], frozen=True):
    def attrs(self, key: str) -> list[Any]:
        return [getattr(m, key) for m in self.root]

    def first(self, key: str, value: Any) -> M:  # noqa: ANN401
        return next(
            filter(
                lambda x: getattr(x, key) == value,
                self.root,
            ),
        )


T = TypeVar("T", bound=BaseModel)


class Composite(BaseModel, Generic[T], frozen=True):
    parent: T
    children: list[Composite[T]] = Field(default_factory=list)

    def get_children(self) -> list[T]:
        return [c.parent for c in self.children]

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, RootModel

from knowde._feature._shared.types import NXGraph  # noqa: TCH001

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


class CompositionTree(BaseModel, Generic[T], frozen=True):
    root: T
    g: NXGraph

    def build(self) -> Composite[T]:
        return self._build(self.root)

    def _build(self, parent: T) -> Composite[T]:
        children = [self._build(n) for n in self.g[parent]]
        return Composite[T](
            parent=parent,
            children=children,
        )

    def children(self, k: T) -> list[T]:
        if k in self.g:
            ls = self.g[k]
            return list(ls)
        return []

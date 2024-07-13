from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, RootModel

from knowde._feature._shared.types import NXGraph  # noqa: TCH001

from .domain import APIReturn, Entity

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


class Composite(APIReturn, Generic[T], frozen=True):
    parent: T
    children: list[Composite[T]] = Field(default_factory=list)


def build_composite(t: type[T], g: NXGraph, parent: T) -> Composite[T]:
    children = [build_composite(t, g, n) for n in g[parent]]
    # ここで型情報を保持してCompositeに渡さないとjson decode時にtype lostする
    return Composite[t](
        parent=parent,
        children=children,
    )


class CompositeTree(APIReturn, Generic[T], frozen=True):
    """Composite builder."""

    # ここで型情報を保持してCompositeに渡さないとjson decode時にtype lostする
    t: type[T]
    root: T
    g: NXGraph

    def build(self) -> Composite[T]:
        return build_composite(self.t, self.g, self.root)

    def children(self, k: T) -> list[T]:
        if k in self.g:
            ls = self.g[k]
            return list(ls)
        return []

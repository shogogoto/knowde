"""コンテナ共通ドメイン."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel, Field, RootModel

from .domain import APIReturn, Entity

if TYPE_CHECKING:
    from knowde.primitive.__core__.types import NXGraph

M = TypeVar("M", bound=Entity)


class ModelList(RootModel[list[M]], frozen=True):
    """モデルのリスト."""

    def attrs(self, key: str) -> list[Any]:
        """属性のみのリスト."""
        return [getattr(m, key) for m in self.root]

    def first(self, key: str, value: Any) -> M:
        """最初の要素."""
        return next(
            filter(
                lambda x: getattr(x, key) == value,
                self.root,
            ),
        )


T = TypeVar("T", bound=BaseModel)


class Composite[T](APIReturn, frozen=True):
    """入れ子."""

    parent: T
    children: list[Composite[T]] = Field(default_factory=list)


def build_composite(t: type[T], g: NXGraph, parent: T) -> Composite[T]:
    """DiGraphから入れ子を作成."""
    children = [build_composite(t, g, n) for n in g[parent]]
    # ここで型情報を保持してCompositeに渡さないとjson decode時にtype lostする
    return Composite[t](
        parent=parent,
        children=children,
    )


class CompositeTree[T](APIReturn, frozen=True):
    """Composite builder."""

    # ここで型情報を保持してCompositeに渡さないとjson decode時にtype lostする
    t: type[T]
    root: T
    g: NXGraph

    def build(self) -> Composite[T]:
        """DiGraphから入れ子を作成."""
        return build_composite(self.t, self.g, self.root)

    def children(self, k: T) -> list[T]:
        """nodeの子供."""
        if k in self.g:
            ls = self.g[k]
            return list(ls)
        return []

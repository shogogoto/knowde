from typing import Generic, TypeVar

from pydantic import BaseModel

from knowde._feature._shared.domain.container import Composite
from knowde._feature._shared.domain.domain import Entity
from knowde._feature._shared.types import NXGraph


class Location(Entity, frozen=True):
    """位置."""

    name: str


T = TypeVar("T", bound=BaseModel)


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

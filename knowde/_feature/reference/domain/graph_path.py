from __future__ import annotations

from typing import Any, Callable, Generic, Hashable, Self, TypeVar

import networkx as nx
from pydantic import BaseModel, Field, model_validator

from knowde._feature._shared.types import Graph

T = TypeVar("T", bound=Hashable)
U = TypeVar("U", bound=Hashable)


class GraphPaths(BaseModel, Generic[T]):
    G: Graph = Field(default_factory=Graph)
    init: list[T] = Field(default_factory=list)

    @model_validator(mode="after")
    def _set_initial_nodes(self) -> Self:
        self.G.add_nodes_from(self.init)
        return self

    def add(self, paths: list[list[T]]) -> None:
        for p in paths:
            nx.add_path(self.G, p)


def _identify(x: Any) -> Any:  # noqa: ANN401
    return x


class GraphReplacer(BaseModel, Generic[T, U]):
    G: Graph = Field(default_factory=Graph)
    init: list[Any] = Field(default_factory=list)
    to_domain: Callable[[Any], T] = _identify  # 定義域 Domain = T
    to_range: Callable[[Any], U] = _identify  # 値域 Range = U

    def __getitem__(self, key: T) -> tuple[U, ...]:
        return tuple(self.G.successors(key))

    @model_validator(mode="after")
    def _set_initial_nodes(self) -> Self:
        for elm in self.init:
            d = self.to_domain(elm)
            r = self.to_range(elm)
            self.add_path((d, r))
        return self

    def add_path(self, path: tuple[T, U]) -> None:
        nx.add_path(self.G, path)

    def __call__(
        self,
        g: Graph,
        # updater: Callable[[T], Any],
    ) -> None:
        mapping = {}
        for ref in g.nodes:
            if ref in self.G:
                mapping[ref] = ref.model_copy(
                    update={
                        "authors": self[ref],
                    },
                )
        nx.relabel_nodes(g, mapping=mapping, copy=False)

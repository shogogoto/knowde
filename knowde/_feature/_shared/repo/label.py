from __future__ import annotations

from typing import Any, Generic, Iterator, TypeVar

from pydantic import (
    BaseModel,
    model_serializer,
)

from knowde._feature._shared.domain import Entity
from knowde._feature._shared.types import NeoModel

L = TypeVar("L", bound=NeoModel)
M = TypeVar("M", bound=Entity)


class Label(BaseModel, Generic[L, M], frozen=True):
    label: L
    model: type[M]

    def to_model(self) -> M:
        return self.model.to_model(self.label)


class Labels(BaseModel, Generic[L, M], frozen=True):
    root: list[L]
    model: type[M]

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self) -> Iterator[L]:
        return iter(self.root)

    def __getitem__(self, i: int) -> L:
        return self.root[i]

    def to_model(self) -> list[M]:
        return [self.model.to_model(lb) for lb in self]

    @model_serializer
    def _serialize(self) -> Any:  # noqa: ANN401
        return [m.model_dump() for m in self.to_model()]

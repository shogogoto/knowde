"""neomodel labelとmodelを対応付ける."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, TypeVar

from pydantic import (
    BaseModel,
    model_serializer,
)

from knowde.shared.domain import Entity
from knowde.shared.types import NeoModel

L = TypeVar("L", bound=NeoModel)
M = TypeVar("M", bound=Entity)


class Label[L, M](BaseModel, frozen=True):
    """neomodel labelとmodelの変換."""

    label: L
    model: type[M]

    def to_model(self) -> M:
        """modelへ変換."""
        return self.model.to_model(self.label)


class Labels[L, M](BaseModel, frozen=True):
    """複数neomodel labelと複数modelの変換."""

    root: list[L]
    model: type[M]

    def __len__(self) -> int:  # noqa: D105
        return len(self.root)

    def __iter__(self) -> Iterator[L]:  # noqa: D105
        return iter(self.root)

    def __getitem__(self, i: int) -> L:  # noqa: D105
        return self.root[i]

    def to_model(self) -> list[M]:
        """modelsへ変換."""
        return [self.model.to_model(lb) for lb in self]

    @model_serializer
    def _serialize(self) -> Any:
        return [m.model_dump() for m in self.to_model()]

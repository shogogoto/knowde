"""neomodel関連Utility."""
from __future__ import annotations

from typing import Generic, Self, TypeAlias, TypeVar
from uuid import UUID

from neomodel import StringProperty, StructuredNode, UniqueIdProperty
from pydantic import BaseModel

from knowde.primitive.__core__.domain.domain import neolabel2model

UUIDy: TypeAlias = UUID | str | UniqueIdProperty  # Falsyみたいな
STRy: TypeAlias = str | StringProperty


def to_uuid(uidy: UUIDy) -> UUID:
    """neomodelのuid propertyがstrを返すからUUIDに補正・統一して扱いたい."""
    return UUID(uidy) if isinstance(uidy, (str, UniqueIdProperty)) else uidy


L = TypeVar("L", bound=StructuredNode)


class BaseMapper(BaseModel, Generic[L], frozen=True):
    """Neomodel-pydantic mapper."""

    __label__: type[L]

    @classmethod
    def from_lb(cls, lb: L) -> Self:
        """Neomodel label to model."""
        return neolabel2model(cls, lb)

    def tolabel(self) -> L:
        """Model to neomodel label."""
        return self.__label__(**self.model_dump())

    @classmethod
    def get_or_none(cls, **kwargs: dict) -> Self | None:
        """Shortcut."""
        lb = cls.__label__.nodes.get_or_none(**kwargs)
        return None if lb is None else cls.from_lb(lb)

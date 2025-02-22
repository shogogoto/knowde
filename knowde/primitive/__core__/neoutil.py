"""neomodel関連Utility."""
from __future__ import annotations

from typing import Generic, Self, TypeVar

from neomodel import StructuredNode
from pydantic import BaseModel

from knowde.primitive.__core__.domain.domain import neolabel2model

L = TypeVar("L", bound=StructuredNode)


class BaseMapper(BaseModel, Generic[L]):
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

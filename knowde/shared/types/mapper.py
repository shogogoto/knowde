"""neomodel関連Utility."""

from __future__ import annotations

from typing import Any, Self, TypeVar

from neomodel import StructuredNode
from pydantic import BaseModel

from knowde.shared.types import NeoModel

T = TypeVar("T", bound=BaseModel)
L = TypeVar("L", bound=StructuredNode)


def neolabel2model[T: BaseModel](
    t: type[T],
    lb: NeoModel,
    attrs: dict | None = None,
) -> T:
    """nemodelのlabelからモデルへ変換."""
    if attrs is None:
        attrs = {}
    return t.model_validate({**lb.__properties__, **attrs})


class NeoMapper[L: StructuredNode](BaseModel):
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
    def get_or_none(cls, **kwargs: dict[str, Any]) -> Self | None:
        """Shortcut."""
        lb = cls.__label__.nodes.get_or_none(**kwargs)
        return None if lb is None else cls.from_lb(lb)

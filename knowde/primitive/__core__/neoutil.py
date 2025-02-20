"""neomodel関連Utility."""
from __future__ import annotations

from typing import Generic, Self, TypeVar

from neomodel import StructuredNode
from pydantic import BaseModel

from knowde.primitive.__core__.domain.domain import neolabel2model

T = TypeVar("T")


class LabelClassNameError(Exception):
    """neomodel labelクラスはLから名前を始めるべし."""


def auto_label(cls: T) -> T:
    """LClassNameからラベル名を設定."""
    if cls.__name__.startswith("L"):
        cls.__label__ = cls.__name__[1:]

    else:
        msg = "クラス名の先頭をLにしてください"
        raise LabelClassNameError(msg, cls.__name__)
    return cls


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

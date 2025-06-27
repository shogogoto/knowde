"""neomodel関連Utility."""

from __future__ import annotations

from typing import TypeVar

from neomodel import StructuredNode
from pydantic import BaseModel

from knowde.shared.types import NeoModel

T = TypeVar("T", bound=BaseModel)
L = TypeVar("L", bound=StructuredNode)


def label2model[T: BaseModel](t: type[T], lb: NeoModel, **kwargs) -> T:
    """nemodelのlabelからモデルへ変換."""
    props = lb.__properties__
    return t.model_validate({**props, **kwargs})


def neolabel2model[T: BaseModel](
    t: type[T],
    lb: NeoModel,
    attrs: dict | None = None,
) -> T:
    """nemodelのlabelからモデルへ変換."""
    if attrs is None:
        attrs = {}
    return t.model_validate({**lb.__properties__, **attrs})

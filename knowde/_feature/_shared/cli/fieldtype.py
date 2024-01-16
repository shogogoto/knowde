from __future__ import annotations

from types import NoneType
from typing import TYPE_CHECKING, Any, TypeGuard, get_args

from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo


def is_nested(annotation: type[Any] | None) -> TypeGuard[type[BaseModel]]:
    types = [type(a) for a in get_args(annotation)]
    if len(types) == 0:
        return isinstance(annotation, type(BaseModel))
    return type(BaseModel) in types


def is_option(info: FieldInfo) -> bool:
    """Optionalではない. かつBaseModelでない."""
    args = get_args(info.annotation)
    if is_nested(info.annotation):
        return False
    return NoneType in args


def extract_type(t: type | None) -> type:
    """NoneTypeを取り除いて返す."""
    if t is None:
        msg = f"{t} must be type"
        raise ValueError(msg)
    args = get_args(t)
    if NoneType in args:
        return next(filter(lambda x: x != NoneType, args))
    return t

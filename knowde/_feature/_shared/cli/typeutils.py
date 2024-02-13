from __future__ import annotations

from types import NoneType
from typing import Any, TypeGuard, get_args

from pydantic import BaseModel


def is_nested(annotation: type[Any] | None) -> TypeGuard[type[BaseModel]]:
    """BaseModel or Optional[BaseModel]のときtrue."""
    types = [type(a) for a in get_args(annotation)]
    if len(types) == 0:
        return isinstance(annotation, type(BaseModel))
    return type(BaseModel) in types


def is_optional(annotation: type[Any] | None) -> bool:
    args = get_args(annotation)
    return NoneType in args


def is_option(annotation: type[Any] | None) -> bool:
    """click.Parameterに変換するよう判定する."""
    if is_nested(annotation):
        return False
    return is_optional(annotation)


def extract_type(t: type | None) -> type:
    """NoneTypeを取り除いて返す."""
    if t is None:
        msg = f"{t} must be type"
        raise ValueError(msg)
    args = get_args(t)
    if NoneType in args:
        return next(filter(lambda x: x != NoneType, args))
    return t

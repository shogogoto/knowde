from types import NoneType
from typing import get_args

from pydantic import BaseModel
from pydantic.fields import FieldInfo


def is_nested(info: FieldInfo) -> bool:
    args = get_args(info.annotation)
    return any(BaseModel in a.__mro__ for a in args)


def is_option(info: FieldInfo) -> bool:
    """Optionalではない. かつBaseModelでない."""
    args = get_args(info.annotation)
    if is_nested(info):
        return False
    return NoneType in args


def extract_type(t: type) -> type:
    """NoneTypeを取り除いて返す."""
    args = get_args(t)
    if NoneType in args:
        return next(filter(lambda x: x != NoneType, args))
    return t

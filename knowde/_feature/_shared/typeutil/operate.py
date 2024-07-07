from __future__ import annotations

from types import NoneType, UnionType
from typing import get_args

from knowde._feature._shared.typeutil.check import is_generic_alias


def extract_type(t: type | None | UnionType) -> type:
    """NoneTypeを取り除いて返す."""
    if t is None:
        msg = f"{t} must be type"
        raise ValueError(msg)
    args = get_args(t)
    if NoneType in args:
        return next(filter(lambda x: x != NoneType, args))
    return t


def extract_generic_alias_type(t: type | None) -> type:
    for arg in get_args(t):
        if not is_generic_alias(arg):
            return arg
    raise TypeError

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeAlias, TypedDict
from uuid import UUID

import click
from click.decorators import FC

from .fieldutils import extract_type

if TYPE_CHECKING:
    from click import ParamType
    from pydantic.fields import FieldInfo

ClickParam: TypeAlias = Callable[[FC], FC]


def to_clicktype(info: FieldInfo) -> ParamType:
    t = extract_type(info.annotation)
    if t == str:
        return click.STRING
    if t == float:
        return click.FLOAT
    if t == UUID:
        return click.UUID
    if t == int:
        return click.INT
    if t == bool:
        return click.BOOL
    msg = f"{t} is not compatible type"
    raise ValueError(msg)


class ClickParamAttrs(TypedDict):
    type: ParamType | Any | None


class OptionAttrs(ClickParamAttrs):
    help: str | None
    # show_default: bool | None


class ArgumentAttrs(ClickParamAttrs):
    pass

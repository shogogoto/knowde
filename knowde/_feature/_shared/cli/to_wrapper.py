from __future__ import annotations

from typing import Callable
from uuid import UUID

import click
from click import ParamType
from pydantic import BaseModel

from knowde._feature._shared.api.param import ApiParam  # noqa: TCH001


def type2type(t: type | None) -> ParamType:
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


Wrapper = Callable[[Callable], Callable]


class ClickWrappers(BaseModel):
    values: list[Wrapper]

    def apply(self, command_func: Callable) -> Callable:
        pass


def to_click_wrappers(
    param: ApiParam,
) -> list[Wrapper]:
    """click.{argument,option}のリストを返す."""
    cliparams = []
    for k, v in param.model_fields.items():
        if v.is_required():
            p = click.argument(
                k,
                nargs=1,
                type=type2type(v.annotation),
            )
        else:
            t = type(getattr(param, k))  # for excliding optional
            p = click.option(
                f"--{k}",
                f"-{k[0]}",
                type=type2type(t),
            )
        cliparams.append(p)
    return cliparams


# def to_wrapped(param: ApiParam) -> Callable:
#     pass

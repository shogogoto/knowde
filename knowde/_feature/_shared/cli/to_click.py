from __future__ import annotations

from typing import Callable, TypeAlias
from uuid import UUID

import click
from click import ParamType
from click.decorators import FC
from pydantic import BaseModel


def to_clicktype(t: type) -> ParamType:
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
    raise TypeError(msg)


ClickParam: TypeAlias = Callable[[FC], FC]


def click_decorate(params: list[ClickParam]) -> ClickParam:
    def _deco(f: FC) -> FC:
        _f = f
        for p in reversed(params):
            _f = p(_f)
        return _f

    return _deco


class ClickDecorator(BaseModel, frozen=True):
    params: list[ClickParam]

    def __call__(self, f: FC) -> FC:
        return click_decorate(self.params)(f)

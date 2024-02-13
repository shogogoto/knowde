from __future__ import annotations

from typing import Callable, TypeAlias
from uuid import UUID

import click
from click import ParamType
from click.decorators import FC
from click.testing import CliRunner
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


class ClickDecorator(BaseModel, frozen=True):
    params: list[ClickParam]

    @property
    def info(self) -> list[tuple[str, str]]:
        @self
        def _dummy() -> None:
            pass

        return [(p.name, p.param_type_name) for p in reversed(_dummy.__click_params__)]

    def show_help(self) -> str:
        """For debugging."""

        @click.command
        @self
        def _dummy() -> None:
            pass

        runner = CliRunner()
        result = runner.invoke(_dummy, ["--help"])
        return result.output

    def __call__(self, f: FC) -> FC:
        _f = f
        for p in reversed(self.params):
            _f = p(_f)
        return _f

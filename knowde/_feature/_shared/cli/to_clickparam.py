from __future__ import annotations

from typing import TYPE_CHECKING

import click
from click.testing import CliRunner
from pydantic import BaseModel
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.cli.fieldtype import (
    extract_type,
    is_nested,
    is_option,
    is_optional,
)

from .types import ArgumentAttrs, ClickParam, to_clicktype

if TYPE_CHECKING:
    from click.decorators import FC
    from pydantic.fields import FieldInfo

    from .types import OptionAttrs


def to_option_attrs(info: FieldInfo) -> OptionAttrs:
    return {
        "type": to_clicktype(info),
        "help": info.description,
    }


def to_argument_attrs(info: FieldInfo) -> ArgumentAttrs:
    return {
        "type": to_clicktype(info),
    }


def to_click_param(
    name: str,
    info: FieldInfo,
) -> ClickParam:
    if is_option(info.annotation):
        return click.option(
            f"--{name}",
            f"-{name[0]}",
            **to_option_attrs(info),
        )
    return click.argument(
        name,
        nargs=1,
        **to_argument_attrs(info),
    )


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


def model2decorator(
    t_model: type[BaseModel],
) -> ClickDecorator:
    params = []
    for k, v in t_model.model_fields.items():
        a = v.annotation
        if is_nested(a):
            if is_optional(a):
                a = extract_type(a)
                a = create_partial_model(a)
            params.extend(model2decorator(a).params)
        else:
            params.append(to_click_param(k, v))
    return ClickDecorator(params=params)

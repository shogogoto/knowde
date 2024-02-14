from __future__ import annotations

from typing import TYPE_CHECKING

import click
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.cli.to_click import (
    ClickDecorator,
    ClickParam,
    to_clicktype,
)
from knowde._feature._shared.cli.typeutils import (
    extract_type,
    is_nested,
    is_option,
    is_optional,
)

if TYPE_CHECKING:
    from pydantic import BaseModel
    from pydantic.fields import FieldInfo

    from .types import ArgumentAttrs, OptionAttrs


def field2option_attrs(info: FieldInfo) -> OptionAttrs:
    return {
        "help": info.description,
        "default": info.default,
    }


def field2argument_attrs(info: FieldInfo) -> ArgumentAttrs:  # noqa: ARG001
    return {}


def to_clickparam(
    name: str,
    info: FieldInfo,
    t: type | None = None,
) -> ClickParam:
    a = info.annotation
    if t is not None:
        a = t
    ct = to_clicktype(extract_type(a))
    if is_option(a):
        return click.option(
            f"--{name}",
            f"-{name[0]}",
            type=ct,
            **field2option_attrs(info),
        )
    return click.argument(
        name,
        nargs=1,
        type=ct,
        **field2argument_attrs(info),
    )


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
            params.append(to_clickparam(k, v))
    return ClickDecorator(params=params)

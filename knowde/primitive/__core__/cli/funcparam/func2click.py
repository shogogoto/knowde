"""関数からclick parameterへの変換."""

from __future__ import annotations

from collections.abc import Callable
from inspect import Parameter, signature
from typing import TYPE_CHECKING

from pydantic.fields import FieldInfo

from knowde.primitive.__core__.cli.field.model2click import (
    model2decorator,
    to_clickparam,
)
from knowde.primitive.__core__.cli.to_click import ClickDecorator
from knowde.primitive.__core__.typeutil import is_nested

if TYPE_CHECKING:
    from knowde.primitive.__core__.cli.to_click import ClickParam


def fparam2clickparams(p: Parameter) -> list[ClickParam]:  # noqa: D103
    name = p.name
    a = p.annotation
    if is_nested(a):
        return model2decorator(a).params

    if isinstance(p.default, FieldInfo):
        return [to_clickparam(name, p.default, a)]
    info = FieldInfo(default=p.default)
    return [to_clickparam(name, info, a)]


def func2clickparams(f: Callable) -> list[ClickParam]:  # noqa: D103
    ret = []
    for fp in signature(f).parameters.values():
        ret += fparam2clickparams(fp)
    return ret


def func2decorator(f: Callable) -> ClickDecorator:  # noqa: D103
    return ClickDecorator(params=func2clickparams(f))

from __future__ import annotations

from inspect import Parameter, signature
from typing import TYPE_CHECKING, Callable

from pydantic.fields import FieldInfo

from knowde._feature._shared.cli.field.model2click import (
    model2decorator,
    to_clickparam,
)
from knowde._feature._shared.cli.typeutils import is_nested

if TYPE_CHECKING:
    from knowde._feature._shared.cli.to_click import ClickParam


def fparam2clickparams(p: Parameter) -> list[ClickParam]:
    name = p.name
    a = p.annotation
    if is_nested(a):
        return model2decorator(a).params

    if isinstance(p.default, FieldInfo):
        return [to_clickparam(name, p.default, a)]
    info = FieldInfo(default=p.default)
    return [to_clickparam(name, info, a)]


def func2clickparams(f: Callable) -> list[ClickParam]:
    ret = []
    for fp in signature(f).parameters.values():
        ret += fparam2clickparams(fp)
    return ret

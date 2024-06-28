from __future__ import annotations

from inspect import Parameter, signature
from typing import Any, Callable, Optional, TypeVar

from makefun import create_function
from pydantic import BaseModel

from knowde._feature._shared.typeutil.func import (
    check_map_fields2params,
)

T = TypeVar("T", bound=BaseModel)


def extract_type_arg(t: type[T], args: tuple, kwargs: dict) -> tuple[T, tuple, dict]:
    """型tの引数を除外する."""
    newargs = []
    newkw = {}
    models = []
    for a in args:
        if isinstance(a, t):
            models.append(a)
        else:
            newargs.append(a)
    for k, v in kwargs.items():
        if isinstance(v, t):
            models.append(v)
        else:
            newkw[k] = v
    return models[0], tuple(newargs), newkw


def to_paramfunc(
    t: type[BaseModel],
    f: Callable,
    argname: str = "param",
    ignores: Optional[list[str]] = None,
) -> Callable:
    """API用関数に変換."""
    if ignores is None:
        ignores = []
    params = dict(signature(f).parameters)
    remains = [params.pop(k) for k in ignores]
    check_map_fields2params(t, params)

    def _f(*args, **kwargs) -> Any:  # noqa: ANN401, ANN003, ANN002
        p, newargs, newkw = extract_type_arg(t, args, kwargs)
        return f(*newargs, **p.model_dump(), **newkw)

    newp = Parameter(argname, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=t)
    return create_function(
        signature(f).replace(parameters=[*remains, newp]),
        _f,
    )

from __future__ import annotations

import functools
from inspect import Parameter, signature
from typing import Any, Callable, Optional, TypeVar

from makefun import create_function
from neomodel import db
from pydantic import BaseModel

from knowde._feature._shared.typeutil.func import (
    check_map_fields2params,
    inject_signature,
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
    convert: Callable = lambda x: x,
) -> Callable:
    """API用関数に変換.

    (*ignores, param: t)の引数に変換
    """
    if ignores is None:
        ignores = []
    params = dict(signature(f).parameters)
    remains = [params.pop(k) for k in ignores]
    check_map_fields2params(t, params)

    @db.transaction
    def _f(*args, **kwargs) -> Any:  # noqa: ANN401, ANN003, ANN002
        p, newargs, newkw = extract_type_arg(t, args, kwargs)
        out = f(*newargs, **p.model_dump(), **newkw)
        return convert(out)

    newp = Parameter(argname, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=t)
    return create_function(
        signature(f).replace(parameters=[*remains, newp]),
        _f,
    )


def to_apifunc(  # noqa: PLR0913
    f: Callable,
    t_param: type[BaseModel],
    t_out: type | None = None,
    paramname: str = "param",
    ignores: Optional[list[tuple[str, type]]] = None,
    convert: Callable = lambda x: x,
) -> Callable:
    """Request bodyを付与する."""
    if ignores is None:
        igkeys, igtypes = [], []
    else:
        igkeys, igtypes = zip(*ignores)
    return inject_signature(
        to_paramfunc(t_param, f, paramname, igkeys, convert),
        [*igtypes, t_param],
        t_out,
        f.__name__,
    )


def to_queryfunc(
    f: Callable,
    t_in: list[type],
    t_out: type | None = None,
    convert: Callable = lambda x: x,
) -> Callable:
    """Query parameterを付与."""

    @functools.wraps(f)
    @db.transaction
    def _f(*args, **kwargs) -> Any:  # noqa: ANN401, ANN003, ANN002
        out = f(*args, **kwargs)
        return convert(out)

    return inject_signature(_f, t_in, t_out)

from __future__ import annotations

from inspect import Parameter, Signature, signature
from typing import Any, Callable, ParamSpec, TypeAlias, TypeVar

from makefun import create_function
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
P = ParamSpec("P")


def flatten_func_params(
    t_in: type[BaseModel],
    # ↓type[BaseModel]の場合、set_router時にundefined-annotation errorになる
    t_out: type | None,
    f: Callable[[T], Any],
    name: str | None = None,
    doc: str | None = None,
) -> Callable:
    params = []
    for k, v in t_in.model_fields.items():
        kind = Parameter.POSITIONAL_OR_KEYWORD
        p = Parameter(k, kind=kind, annotation=v.annotation)
        params.append(p)

    def _f(**kwargs) -> t_out:  # noqa: ANN003
        if t_in is not None:
            model = t_in.model_validate(kwargs)
            return f(model)
        return f()

    return create_function(
        signature(f).replace(
            parameters=params,
            return_annotation=t_out,
        ),
        _f,
        func_name=name,
        doc=doc,
    )


def eval_signature(
    t_in: type[BaseModel] | None,
    t_out: type[BaseModel],
    func: Callable,
    name: str | None = None,
    doc: str | None = None,
) -> Callable:
    func = create_function(signature(func), func)
    params = signature(func).parameters
    p = next(iter(params.values()))
    return func
    return create_function(
        # signature(func),
        Signature(
            # parameters=params,
            parameters=[
                p.replace(annotation=t_in),
            ],
            return_annotation=t_out,
        ),
        func,
        name,
        doc,
    )


Decorator: TypeAlias = Callable[[Callable], Callable]


def change_signature(
    t_in: type[BaseModel] | None,
    t_out: type[BaseModel],
    name: str | None = None,
    doc: str | None = None,
    just_eval: bool = False,  # noqa: FBT001 FBT002
) -> Decorator:
    """fastapi起動時のundefined annotation回避のために必要."""

    def _decorator(func: Callable[[t_in], t_out]) -> Callable:
        if t_in is None:
            return create_function(Signature(return_annotation=t_out), func, name, doc)
        if just_eval:
            return eval_signature(t_in, t_out, func, name, doc)
        return flatten_func_params(t_in, t_out, func, name, doc)

    return _decorator

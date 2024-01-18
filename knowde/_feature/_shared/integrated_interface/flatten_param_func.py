from __future__ import annotations

from inspect import Parameter, signature
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from makefun import create_function

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar("T", bound=DomainModel)
P = ParamSpec("P")


# Python 3.12で関数のGenericが導入されたらリライト
def flatten_param_func(
    t_in: type[BaseModel] | None,
    # ↓type[BaseModel]の場合、set_router時にundefined-annotation errorになる
    t_out: type | None,
    f: Callable[[BaseModel], Any],
    name: str | None = None,
    doc: str | None = None,
) -> Callable:
    params = []
    if t_in is not None:
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

from __future__ import annotations

from inspect import Parameter, signature
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

from makefun import create_function

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from pydantic import BaseModel


T = TypeVar("T", bound=DomainModel)
P = ParamSpec("P")


def parametrize(
    mdl: type[BaseModel],
    f: Callable[P, T],
    func_name: str | None = None,
    doc: str | None = None,
    exclude: bool = False,  # noqa: FBT001 FBT002
) -> Callable[P, T]:
    params = []
    for k, v in mdl.model_fields.items():
        if exclude and v.exclude:
            continue
        kind = Parameter.POSITIONAL_OR_KEYWORD
        p = Parameter(k, kind=kind, annotation=v.annotation)
        params.append(p)

    def impl(**kwargs) -> T:  # noqa: ANN003
        return f(**kwargs)

    return create_function(
        signature(f).replace(parameters=params),
        impl,
        func_name=func_name,
        doc=doc,
    )

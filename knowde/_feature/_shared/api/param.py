from __future__ import annotations

from inspect import Parameter, Signature, signature
from typing import TYPE_CHECKING, Callable, Generic, Self, TypeVar

from makefun import create_function
from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from knowde._feature._shared.repo.base import LBase

T = TypeVar("T", bound=DomainModel)


class ApiParam(BaseModel, Generic[T], frozen=True):
    def set_attr(self, lb: LBase) -> None:
        for k, v in self.model_fields:
            setattr(lb, k, v)

    @classmethod
    def makefunc(
        cls,
        f: Callable[[Self], T],
        func_name: str | None = None,
        doc: str | None = None,
    ) -> Callable:
        params = []
        for k, v in cls.model_fields.items():
            kind = Parameter.KEYWORD_ONLY
            p = Parameter(k, kind=kind, annotation=v.annotation)
            params.append(p)
        r = signature(f).return_annotation
        sig = Signature(params, return_annotation=r)

        def impl(**kwargs) -> T:  # noqa: ANN003
            return f(cls(**kwargs))

        return create_function(
            sig,
            impl,
            func_name=func_name,
            doc=doc,
        )

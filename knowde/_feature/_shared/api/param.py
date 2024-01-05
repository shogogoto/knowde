from __future__ import annotations

from inspect import Parameter, signature
from typing import TYPE_CHECKING, Callable, Generic, ParamSpec, TypeVar

from makefun import create_function
from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from fastapi import APIRouter

    from knowde._feature._shared.repo.base import LBase

T = TypeVar("T", bound=DomainModel)
P = ParamSpec("P")


class ApiParam(BaseModel, Generic[T], frozen=True):
    def set_attr(self, lb: LBase) -> None:
        for k, v in self.model_fields:
            setattr(lb, k, v)

    @classmethod
    def makefunc(
        cls,
        f: Callable[P, T],
        func_name: str | None = None,
        doc: str | None = None,
    ) -> Callable[P, T]:
        params = []
        for k, v in cls.model_fields.items():
            kind = Parameter.KEYWORD_ONLY
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

    @classmethod
    def api(
        cls,
        router: APIRouter,
        func: Callable,
        name: str | None = None,
        doc: str | None = None,
    ) -> APIRouter:
        f = cls.makefunc(func, func_name=name, doc=doc)
        cls.api_impl(router, f)
        return router

    @classmethod
    def api_impl(cls, router: APIRouter, func: Callable) -> None:
        pass

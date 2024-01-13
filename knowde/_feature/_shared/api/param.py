from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    ParamSpec,
    TypedDict,
    TypeVar,
)

from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.param import parametrize

if TYPE_CHECKING:
    from fastapi import APIRouter

    from knowde._feature._shared.repo.base import LBase

T = TypeVar("T", bound=DomainModel)
P = ParamSpec("P")


class HttpMethodParams(TypedDict):
    relative: str | None
    params: dict | None
    json: object


class ApiParam(BaseModel, Generic[T], frozen=True):
    def set_attr(self, lb: LBase) -> None:
        for k, v in self.model_fields:
            setattr(lb, k, v)

    @classmethod
    def api(
        cls,
        router: APIRouter,
        func: Callable,
        name: str | None = None,
        doc: str | None = None,
    ) -> APIRouter:
        """FastAPIでエンドポイントを定義."""
        f = parametrize(cls, func, func_name=name, doc=doc, exclude=True)
        cls.api_impl(router, f)
        return router

    @classmethod
    def api_impl(cls, router: APIRouter, func: Callable) -> None:
        pass

    @classmethod
    def for_method(cls, **kwargs) -> HttpMethodParams:  # noqa: ARG003 ANN003
        return {"relative": None, "params": None, "json": None}

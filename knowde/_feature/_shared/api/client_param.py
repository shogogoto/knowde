from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Self, TypeVar

from pydantic import BaseModel
from typing_extensions import override

from knowde._feature._shared.api.errors import RequestParamBindError

if TYPE_CHECKING:
    from knowde._feature._shared.api.types import RequestMethod, ToRequest

T = TypeVar("T")


class APIParam(ABC):
    @abstractmethod
    def getvalue(self, kwargs: dict) -> Any:  # noqa: ANN401
        raise NotImplementedError


class PathParam(BaseModel, APIParam, frozen=True):
    """relative引数と紐づく."""

    name: str
    prefix: str | None = None

    @property
    def var(self) -> str:
        return f"{{{self.name}}}"

    @property
    def path(self) -> str:
        if self.prefix is None:
            return f"/{self.var}"
        return f"/{self.prefix}/{self.var}"

    def bind(self, to_req: ToRequest, f: Callable) -> RequestMethod:
        return to_req(f, path=self.path)

    def getvalue(self, kwargs: dict) -> Any:  # noqa: ANN401
        if self.name not in kwargs:
            msg = f"{self.name}は{list(kwargs.keys())}に含まれていません"
            raise RequestParamBindError(msg)
        return kwargs.get(self.name)


class QueryParam(BaseModel, APIParam, frozen=True):
    """params引数と紐づく."""

    name: str

    def combine(self, other: Self) -> ComplexQueryParam:
        return ComplexQueryParam(members=[self, other])

    @override
    def getvalue(self, kwargs: dict) -> dict:
        if self.name not in kwargs:
            msg = f"{self.name}は{list(kwargs.keys())}に含まれていません"
            raise RequestParamBindError(msg)
        return {self.name: kwargs.get(self.name)}


class ComplexQueryParam(BaseModel, APIParam, frozen=True):
    """params引数と紐づく."""

    members: list[QueryParam | ComplexQueryParam]

    def combine(self, other: QueryParam | ComplexQueryParam) -> ComplexQueryParam:
        if isinstance(other, QueryParam):
            return ComplexQueryParam(members=[*self.members, other])
        return ComplexQueryParam(members=self.members + other.members)

    @override
    def getvalue(self, kwargs: dict) -> dict:
        d = {}
        for mbr in self.members:
            d.update(mbr.getvalue(kwargs))
        return d


class BodyParam(BaseModel, APIParam, frozen=True):
    """json引数と紐づく."""

    annotation: type[BaseModel]

    def getvalue(self, kwargs: dict) -> dict:
        self.annotation.model_rebuild()
        d = {}
        for k in self.annotation.model_fields:
            if k not in kwargs:
                msg = f"{k}は{list(kwargs.keys())}に含まれていません"
                raise RequestParamBindError(msg)
            d[k] = kwargs[k]
        return self.annotation.model_validate(d).model_dump()

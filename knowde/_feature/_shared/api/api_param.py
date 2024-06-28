from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Self,
)

from pydantic import BaseModel, Field
from typing_extensions import override

from knowde._feature._shared.api.errors import APIParamBindError

if TYPE_CHECKING:
    from fastapi import APIRouter

    from knowde._feature._shared.api.types import (
        EndpointMethod,
        Router2EndpointMethod,
        ToEndpointMethod,
    )


class APIParam(ABC):
    @abstractmethod
    def getvalue(self, kwargs: dict) -> Any:  # noqa: ANN401
        raise NotImplementedError


class BaseAPIPath(APIParam):
    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    def to_endpoint_method(
        self,
        router: APIRouter,
        r2epm: Router2EndpointMethod,
        f: Callable,
    ) -> EndpointMethod:
        return r2epm(router, f, self.path)


class APIPath(BaseModel, BaseAPIPath, frozen=True):
    """relative引数と紐づく."""

    name: str
    prefix: str = ""
    is_null: bool = Field(default=False)

    @property
    def var(self) -> str:
        if self.name == "":
            return ""
        if self.is_null:
            return ""
        return f"{{{self.name}}}"

    @property
    def path(self) -> str:
        if self.is_null:
            return self.prefix
        p = []
        p.extend(self.prefix.split("/"))
        p.extend(self.var.split("/"))
        return "/" + "/".join([e for e in p if e != ""])

    def getvalue(self, kwargs: dict) -> str:
        if self.is_null:
            return ""
        if self.name == "":
            return self.path
        if self.name not in kwargs:
            msg = f"{self.name}は{list(kwargs.keys())}に含まれていません"
            raise APIParamBindError(msg)
        v = kwargs.get(self.name)
        return self.path.replace(self.var, f"{v}")

    @classmethod
    @cache
    def null(cls) -> APIPath:
        return cls(name="dummy", is_null=True)

    def combine(self, other: Self) -> ComplexAPIPath:
        return ComplexAPIPath(members=[self, other])

    def add(self, name: str = "", prefix: str = "") -> ComplexAPIPath:
        return self.combine(self.__class__(name=name, prefix=prefix))


class ComplexAPIPath(BaseModel, BaseAPIPath, frozen=True):
    """relative引数と紐づく."""

    members: list[APIPath | ComplexAPIPath] | list[APIPath]

    @property
    def path(self) -> str:
        let = []
        for p in [p.path for p in self.members]:
            let.extend(p.split("/"))
        return "/" + "/".join([e for e in let if e != ""])

    def bind(self, to_req: ToEndpointMethod, f: Callable) -> EndpointMethod:
        return to_req(f, path=self.path)

    def combine(self, other: APIPath | ComplexAPIPath) -> ComplexAPIPath:
        if isinstance(other, APIPath):
            return ComplexAPIPath(members=[*self.members, other])
        return ComplexAPIPath(members=self.members + other.members)

    @override
    def getvalue(self, kwargs: dict) -> str:
        vs = [p.getvalue(kwargs) for p in self.members]
        return "".join([v for v in vs if v])

    def add(self, name: str = "", prefix: str = "") -> ComplexAPIPath:
        return self.combine(APIPath(name=name, prefix=prefix))


class APIQuery(BaseModel, APIParam, frozen=True):
    """params引数と紐づく."""

    name: str

    def combine(self, other: Self) -> ComplexAPIQuery:
        return ComplexAPIQuery(members=[self, other])

    @override
    def getvalue(self, kwargs: dict) -> dict:
        if self.name not in kwargs:
            msg = f"{self.name}は{list(kwargs.keys())}に含まれていません"
            raise APIParamBindError(msg)
        return {self.name: kwargs.get(self.name)}

    def add(self, name: str) -> ComplexAPIQuery:
        return self.combine(self.__class__(name=name))


class ComplexAPIQuery(BaseModel, APIParam, frozen=True):
    """params引数と紐づく."""

    members: list[APIQuery | ComplexAPIQuery]

    def combine(self, other: APIQuery | ComplexAPIQuery) -> ComplexAPIQuery:
        if isinstance(other, APIQuery):
            return ComplexAPIQuery(members=[*self.members, other])
        return ComplexAPIQuery(members=self.members + other.members)

    @override
    def getvalue(self, kwargs: dict) -> dict:
        d = {}
        for mbr in self.members:
            d.update(mbr.getvalue(kwargs))
        return d

    def add(self, name: str) -> ComplexAPIQuery:
        return self.combine(APIQuery(name=name))


class APIBody(BaseModel, APIParam, frozen=True):
    """json引数と紐づく."""

    annotation: type[BaseModel]
    is_null: bool = Field(default=False)

    def getvalue(self, kwargs: dict) -> dict:
        if self.is_null:
            return {}
        self.annotation.model_rebuild()
        d = {}
        for k in self.annotation.model_fields:
            if k not in kwargs:
                msg = f"{k}は{list(kwargs.keys())}に含まれていません"
                raise APIParamBindError(msg)
            d[k] = kwargs[k]
        return self.annotation.model_validate(d).model_dump(mode="json")

    @classmethod
    @cache
    def null(cls) -> Self:
        return cls(
            annotation=BaseModel,  # dummy argument
            is_null=True,
        )

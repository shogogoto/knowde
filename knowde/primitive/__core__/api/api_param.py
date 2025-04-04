"""API定義用パラメータ."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    override,
)

from pydantic import BaseModel, Field

from knowde.primitive.__core__.api.check_response import check_default
from knowde.primitive.__core__.api.errors import APIParamBindError

if TYPE_CHECKING:
    import requests
    from fastapi import APIRouter

    from knowde.primitive.__core__.api.types import (
        CheckResponse,
        ClientRequest,
        EndpointMethod,
        Router2EndpointMethod,
        ToEndpointMethod,
    )


class APIParam(ABC):
    """APIパラメータインターフェース."""

    @abstractmethod
    def getvalue(self, kwargs: dict) -> Any:
        """requestに必要なパラメータ値を取得."""
        raise NotImplementedError


class NullParam(BaseModel, APIParam):
    """空を返す."""

    @staticmethod
    def getvalue(kwargs: dict) -> Any:  # noqa: ARG004
        """値を取得."""
        return {}


T = TypeVar("T")


class BaseAPIPath(BaseModel, APIParam, frozen=True):
    """APIPathの抽象クラス."""

    @property
    @abstractmethod
    def path(self) -> str:
        """パスを返す."""
        raise NotImplementedError

    def to_request(
        self,
        router: APIRouter,
        r2epm: Router2EndpointMethod,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | NullParam | None = None,
        t_body: type[BaseModel] | None = None,
    ) -> ClientRequest:
        """APIにリクエスト."""
        epm = r2epm(router, f, path=self.path)
        if query is None:
            query = NullParam()

        apibody = NullParam() if t_body is None else APIBody(annotation=t_body)

        def _request(**kwargs) -> requests.Response:
            return epm(
                relative=self.getvalue(kwargs),
                params=query.getvalue(kwargs),
                json=apibody.getvalue(kwargs),
            )

        return _request

    def to_client(  # noqa: PLR0917
        self,
        router: APIRouter,
        r2epm: Router2EndpointMethod,
        f: Callable,
        convert: Callable[[requests.Response], T],
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: list[CheckResponse] | None = None,
    ) -> Callable[..., T]:
        """APIResponseを解決して返す."""
        if check_responses is None:
            check_responses = []
        req = self.to_request(router, r2epm, f, query=query, t_body=t_body)

        def _client(**kwargs) -> T:
            res = req(**kwargs)
            for c in [check_default(r2epm), *check_responses]:
                c(res)
            return convert(res)

        return _client


class NullPath(BaseAPIPath, frozen=True):
    """空のパスパラメータ."""

    @property
    def path(self) -> str:
        """パスを取得."""
        return ""

    def getvalue(self, kwargs: dict) -> str:  # noqa: ARG002, D102, PLR6301
        return ""


class APIPath(BaseAPIPath, frozen=True):
    """relative引数と紐づく."""

    name: str = Field("")
    prefix: str = Field("")

    @property
    def var(self) -> str:
        """パスパラメータ名."""
        if not self.name:
            return ""
        return f"{{{self.name}}}"

    @property
    def path(self) -> str:  # noqa: D102
        p = []
        p.extend(self.prefix.split("/"))
        p.extend(self.var.split("/"))
        return "/" + "/".join([e for e in p if e])

    def getvalue(self, kwargs: dict) -> str:  # noqa: D102
        if not self.name:
            return self.path
        if self.name not in kwargs:
            msg = f"{self.name}は{list(kwargs.keys())}に含まれていません"
            raise APIParamBindError(msg)
        v = kwargs.get(self.name)
        return self.path.replace(self.var, f"{v}")

    def add(self, name: str = "", prefix: str = "") -> ComplexAPIPath:
        """パスを合成."""
        other = self.__class__(name=name, prefix=prefix)
        return ComplexAPIPath(members=[self, other])


class ComplexAPIPath(BaseAPIPath, frozen=True):
    """relative引数と紐づく."""

    members: list[APIPath | ComplexAPIPath] | list[APIPath]

    @property
    def path(self) -> str:  # noqa: D102
        let = []
        for p in [p.path for p in self.members]:
            let.extend(p.split("/"))
        return "/" + "/".join([e for e in let if e])

    def bind(self, to_req: ToEndpointMethod, f: Callable) -> EndpointMethod:  # noqa: D102
        return to_req(f, path=self.path)

    @override
    def getvalue(self, kwargs: dict) -> str:
        vs = [p.getvalue(kwargs) for p in self.members]
        return "".join([v for v in vs if v])

    def add(self, name: str = "", prefix: str = "") -> ComplexAPIPath:  # noqa: D102
        other = APIPath(name=name, prefix=prefix)
        return ComplexAPIPath(members=[*self.members, other])


class APIQuery(BaseModel, APIParam, frozen=True):
    """params引数と紐づく."""

    name: str

    @override
    def getvalue(self, kwargs: dict) -> dict:
        if self.name not in kwargs:
            msg = f"{self.name}は{list(kwargs.keys())}に含まれていません"
            raise APIParamBindError(msg)
        return {self.name: kwargs.get(self.name)}

    def add(self, name: str) -> ComplexAPIQuery:  # noqa: D102
        other = self.__class__(name=name)
        return ComplexAPIQuery(members=[self, other])


class ComplexAPIQuery(BaseModel, APIParam, frozen=True):
    """params引数と紐づく."""

    members: list[APIQuery | ComplexAPIQuery]

    @override
    def getvalue(self, kwargs: dict) -> dict:
        d = {}
        for mbr in self.members:
            d.update(mbr.getvalue(kwargs))
        return d

    def add(self, name: str) -> ComplexAPIQuery:  # noqa: D102
        other = APIQuery(name=name)
        return ComplexAPIQuery(members=[*self.members, other])


class APIBody(BaseModel, APIParam, frozen=True):
    """json引数と紐づく."""

    annotation: type[BaseModel]

    def getvalue(self, kwargs: dict) -> dict:  # noqa: D102
        self.annotation.model_rebuild()
        d = {}
        for k in self.annotation.model_fields:
            if k not in kwargs:
                msg = f"{k}は{list(kwargs.keys())}に含まれていません"
                raise APIParamBindError(msg)
            d[k] = kwargs[k]
        return self.annotation.model_validate(d).model_dump(mode="json")

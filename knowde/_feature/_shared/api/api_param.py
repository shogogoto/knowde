from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    TypeVar,
)

from pydantic import BaseModel, Field
from typing_extensions import override

from knowde._feature._shared.api.check_response import check_default
from knowde._feature._shared.api.errors import APIParamBindError

if TYPE_CHECKING:
    import requests
    from fastapi import APIRouter

    from knowde._feature._shared.api.types import (
        CheckResponse,
        ClientRequest,
        EndpointMethod,
        Router2EndpointMethod,
        ToEndpointMethod,
    )


class APIParam(ABC):
    @abstractmethod
    def getvalue(self, kwargs: dict) -> Any:  # noqa: ANN401
        raise NotImplementedError


class NullParam(BaseModel, APIParam):
    def getvalue(self, kwargs: dict) -> Any:  # noqa: ANN401 ARG002
        return {}


T = TypeVar("T")


class BaseAPIPath(BaseModel, APIParam, frozen=True):
    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    def to_request(  # noqa: PLR0913
        self,
        router: APIRouter,
        r2epm: Router2EndpointMethod,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | NullParam | None = None,
        t_body: type[BaseModel] | None = None,
    ) -> ClientRequest:
        epm = r2epm(router, f, path=self.path)
        if query is None:
            query = NullParam()

        apibody = NullParam() if t_body is None else APIBody(annotation=t_body)

        def _request(**kwargs) -> requests.Response:  # noqa: ANN003
            return epm(
                relative=self.getvalue(kwargs),
                params=query.getvalue(kwargs),
                json=apibody.getvalue(kwargs),
            )

        return _request

    def to_client(  # noqa: PLR0913
        self,
        router: APIRouter,
        r2epm: Router2EndpointMethod,
        f: Callable,
        convert: Callable[[requests.Response], T],
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: Optional[list[CheckResponse]] = None,
    ) -> Callable[..., T]:
        if check_responses is None:
            check_responses = []
        req = self.to_request(router, r2epm, f, query=query, t_body=t_body)

        def _client(**kwargs) -> T:  # noqa: ANN003
            res = req(**kwargs)
            for c in [check_default(r2epm), *check_responses]:
                c(res)
            return convert(res)

        return _client


class NullPath(BaseAPIPath, frozen=True):
    @property
    def path(self) -> str:
        return ""

    def getvalue(self, kwargs: dict) -> str:  # noqa: ARG002
        return ""


class APIPath(BaseAPIPath, frozen=True):
    """relative引数と紐づく."""

    name: str = Field("")
    prefix: str = Field("")

    @property
    def var(self) -> str:
        if self.name == "":
            return ""
        return f"{{{self.name}}}"

    @property
    def path(self) -> str:
        p = []
        p.extend(self.prefix.split("/"))
        p.extend(self.var.split("/"))
        return "/" + "/".join([e for e in p if e != ""])

    def getvalue(self, kwargs: dict) -> str:
        if self.name == "":
            return self.path
        if self.name not in kwargs:
            msg = f"{self.name}は{list(kwargs.keys())}に含まれていません"
            raise APIParamBindError(msg)
        v = kwargs.get(self.name)
        return self.path.replace(self.var, f"{v}")

    def add(self, name: str = "", prefix: str = "") -> ComplexAPIPath:
        other = self.__class__(name=name, prefix=prefix)
        return ComplexAPIPath(members=[self, other])


class ComplexAPIPath(BaseAPIPath, frozen=True):
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

    @override
    def getvalue(self, kwargs: dict) -> str:
        vs = [p.getvalue(kwargs) for p in self.members]
        return "".join([v for v in vs if v])

    def add(self, name: str = "", prefix: str = "") -> ComplexAPIPath:
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

    def add(self, name: str) -> ComplexAPIQuery:
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

    def add(self, name: str) -> ComplexAPIQuery:
        other = APIQuery(name=name)
        return ComplexAPIQuery(members=[*self.members, other])


class APIBody(BaseModel, APIParam, frozen=True):
    """json引数と紐づく."""

    annotation: type[BaseModel]

    def getvalue(self, kwargs: dict) -> dict:
        self.annotation.model_rebuild()
        d = {}
        for k in self.annotation.model_fields:
            if k not in kwargs:
                msg = f"{k}は{list(kwargs.keys())}に含まれていません"
                raise APIParamBindError(msg)
            d[k] = kwargs[k]
        return self.annotation.model_validate(d).model_dump(mode="json")

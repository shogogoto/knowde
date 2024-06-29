from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, Self, TypeVar

from fastapi import APIRouter  # noqa: TCH002
from pydantic import BaseModel, Field

from knowde._feature._shared.api.check_response import (
    check_delete,
    check_get,
    check_post,
    check_put,
)
from knowde._feature._shared.api.generate_req import StatusCodeGrant
from knowde._feature._shared.domain import APIReturn

from .api_param import (
    APIBody,
    APIPath,
    APIQuery,
    BaseAPIPath,
    ComplexAPIPath,
    ComplexAPIQuery,
    NullParam,
    NullPath,
)

if TYPE_CHECKING:
    import requests

    from knowde._feature._shared.api.types import (
        CheckResponse,
        ClientRequest,
        EndpointMethod,
        ToEndpointMethod,
    )

T = TypeVar("T")


def none_return(_res: requests.Response) -> None:
    pass


def to_request(
    epm: EndpointMethod,
    apipath: BaseAPIPath = NullPath(),
    apiquery: APIQuery | ComplexAPIQuery | NullParam = NullParam(),
    apibody: APIBody | NullParam = NullParam(),
) -> ClientRequest:
    def _request(**kwargs) -> requests.Response:  # noqa: ANN003
        return epm(
            relative=apipath.getvalue(kwargs),
            params=apiquery.getvalue(kwargs),
            json=apibody.getvalue(kwargs),
        )

    return _request


def to_client(
    req: ClientRequest,
    convert: Callable[[requests.Response], T],
    *check_response: CheckResponse,
) -> Callable[..., T]:
    def _client(**kwargs) -> T:  # noqa: ANN003
        res = req(**kwargs)
        for c in check_response:
            c(res)
        return convert(res)

    return _client


class RouterConfig(BaseModel):
    """APIパラメータのMediator."""

    paths_: list[APIPath] = Field(
        default_factory=list,
        init_var=False,
    )
    queries_: list[APIQuery | ComplexAPIQuery] = Field(
        default_factory=list,
        init_var=False,
    )
    body_: APIBody | NullParam = Field(default_factory=NullParam)

    @property
    def pathparam(self) -> BaseAPIPath:
        p = ComplexAPIPath(members=self.paths_)
        if len(self.paths_) == 0:
            p = NullPath()
        return p

    def __call__(
        self,
        to_req: ToEndpointMethod,
        f: Callable,
    ) -> Callable[..., requests.Response]:
        return to_request(
            to_req(f, self.pathparam.path),
            self.pathparam,
            ComplexAPIQuery(members=self.queries_),
            self.body_,
        )

        # def _request(**kwargs) -> requests.Response:
        #     return req(
        #         relative=self.pathparam.getvalue(kwargs),
        #         params=ComplexAPIQuery(members=self.queries_).getvalue(kwargs),
        #         json=self.body_.getvalue(kwargs),
        #     )

    def to_client(
        self,
        to_req: ToEndpointMethod,
        f: Callable,
        convert: Callable[[requests.Response], T],
        *check_response: CheckResponse,
    ) -> Callable[..., T]:
        req = self(
            to_req,
            f,
        )

        def _client(**kwargs) -> T:  # noqa: ANN003
            res = req(**kwargs)
            for c in check_response:
                c(res)
            return convert(res)

        return _client

    def path(self, name: str = "", prefix: str = "") -> Self:
        self.paths_.append(APIPath(name=name, prefix=prefix))
        return self

    def query(self, name: str) -> Self:
        self.queries_.append(APIQuery(name=name))
        return self

    def body(self, annotation: type[BaseModel]) -> Self:
        self.body_ = APIBody(annotation=annotation)
        return self


U = TypeVar("U", bound=APIReturn)


class ClientFactory(
    BaseModel,
    Generic[U],
    frozen=True,
    arbitrary_types_allowed=True,
):
    """RouterConfigを利用してちょっと簡単にAPIClientを作る."""

    router: APIRouter
    rettype: type[U]

    @property
    def grant(self) -> StatusCodeGrant:
        return StatusCodeGrant(router=self.router)

    def to_gets(
        self,
        config: RouterConfig,
        f: Callable[..., U],
        *check_response: CheckResponse,
    ) -> Callable[..., list[U]]:
        """listを返すget method client."""
        return config.to_client(
            self.grant.to_get,
            f,
            self.rettype.ofs,
            *[check_get, *check_response],
        )

    def to_get(
        self,
        config: RouterConfig,
        f: Callable[..., U],
        *check_response: CheckResponse,
    ) -> Callable[..., U]:
        """単一要素を返すget method client."""
        return config.to_client(
            self.grant.to_get,
            f,
            self.rettype.of,
            *[check_get, *check_response],
        )

    def to_post(
        self,
        config: RouterConfig,
        f: Callable[..., U],
        *check_response: CheckResponse,
    ) -> Callable[..., U]:
        return config.to_client(
            self.grant.to_post,
            f,
            self.rettype.of,
            *[check_post, *check_response],
        )

    def to_put(
        self,
        config: RouterConfig,
        f: Callable[..., U],
        *check_response: CheckResponse,
    ) -> Callable[..., U]:
        return config.to_client(
            self.grant.to_put,
            f,
            self.rettype.of,
            *[check_put, *check_response],
        )

    def to_delete(
        self,
        config: RouterConfig,
        f: Callable[..., None],
        *check_response: CheckResponse,
    ) -> Callable[..., None]:
        return config.to_client(
            self.grant.to_delete,
            f,
            none_return,
            *[check_delete, *check_response],
        )

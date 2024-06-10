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
from knowde._feature._shared.api.client_param import (
    BodyParam,
    ComplexPathParam,
    ComplexQueryParam,
    PathParam,
    QueryParam,
)
from knowde._feature._shared.api.generate_req import StatusCodeGrant
from knowde._feature._shared.domain import APIReturn

if TYPE_CHECKING:
    import requests

    from knowde._feature._shared.api.types import (
        CheckResponse,
        ToRequest,
    )

T = TypeVar("T")


class RouterConfig(BaseModel):
    """APIパラメータのMediator."""

    paths_: list[PathParam] = Field(
        default_factory=list,
        init_var=False,
    )
    queries_: list[QueryParam | ComplexQueryParam] = Field(
        default_factory=list,
        init_var=False,
    )
    body_: BodyParam = Field(default_factory=BodyParam.null, init_var=False)

    def __call__(
        self,
        to_req: ToRequest,
        f: Callable,
    ) -> Callable[..., requests.Response]:
        p = ComplexPathParam(members=self.paths_)
        if len(self.paths_) == 0:
            p = PathParam.null()
        req = p.bind(to_req, f)

        def _request(**kwargs) -> requests.Response:  # noqa: ANN003
            return req(
                relative=p.getvalue(kwargs),
                params=ComplexQueryParam(members=self.queries_).getvalue(kwargs),
                json=self.body_.getvalue(kwargs),
            )

        return _request

    def to_client(
        self,
        to_req: ToRequest,
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
        self.paths_.append(PathParam(name=name, prefix=prefix))
        return self

    def query(self, name: str) -> Self:
        self.queries_.append(QueryParam(name=name))
        return self

    def body(self, annotation: type[BaseModel]) -> Self:
        self.body_ = BodyParam(annotation=annotation)
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
        def convert(_res: requests.Response) -> None:
            return None

        return config.to_client(
            self.grant.to_delete,
            f,
            convert,
            *[check_delete, *check_response],
        )

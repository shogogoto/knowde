from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Self, TypeVar

from compose import compose
from pydantic import BaseModel, Field

from knowde._feature._shared.api.client_param import (
    BodyParam,
    ComplexQueryParam,
    PathParam,
    QueryParam,
)
from knowde._feature._shared.domain import APIReturn

if TYPE_CHECKING:
    import requests

    from knowde._feature._shared.api.types import (
        ToRequest,
    )


class RequestPartial(BaseModel):
    """APIパラメータのMediator."""

    path_: PathParam = Field(default_factory=PathParam.null, init=False)
    queries_: list[QueryParam | ComplexQueryParam] = Field(
        default_factory=list,
        init=False,
    )
    body_: BodyParam = Field(default_factory=BodyParam.null, init=False)

    def __call__(
        self,
        to_req: ToRequest,
        f: Callable,
    ) -> Callable[..., requests.Response]:
        req = self.path_.bind(to_req, f)

        def _client(**kwargs) -> requests.Response:  # noqa: ANN003
            return req(
                relative=self.path_.getvalue(kwargs),
                params=ComplexQueryParam(members=self.queries_).getvalue(kwargs),
                json=self.body_.getvalue(kwargs),
            )

        return _client

    def path(self, name: str, prefix: str = "") -> Self:
        self.path_ = PathParam(name=name, prefix=prefix)
        return self

    def query(self, name: str) -> Self:
        self.queries_.append(QueryParam(name=name))
        return self

    def body(self, annotation: type[BaseModel]) -> Self:
        self.body_ = BodyParam(annotation=annotation)
        return self


T = TypeVar("T", bound=APIReturn)


def to_client(
    req: Callable[..., requests.Response],
    t: type[T],
) -> Callable[..., T]:
    return compose(t.of, req)


def to_client_return_list(
    req: Callable[..., requests.Response],
    t: type[T],
) -> Callable[..., list[T]]:
    return compose(t.ofs, req)

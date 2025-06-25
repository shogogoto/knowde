"""API Client for CLI."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel

from knowde.shared.api.endpoint import (
    router2delete,
    router2get,
    router2put,
    router2tpost,
)
from knowde.shared.domain import APIReturn

if TYPE_CHECKING:
    from knowde.shared.api.api_param import (
        APIQuery,
        BaseAPIPath,
        ComplexAPIQuery,
    )
    from knowde.shared.api.types import CheckResponse

T = TypeVar("T", bound=APIReturn)


class ClientFactory[T](
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    """to_clientをちょっと楽に."""

    router: APIRouter
    rettype: type[T]

    def get(
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: list[CheckResponse] | None = None,
    ) -> Callable[..., T]:
        """Get client."""
        return p.to_client(
            router=self.router,
            r2epm=router2get,
            f=f,
            convert=self.rettype.of,
            query=query,
            t_body=t_body,
            check_responses=check_responses,
        )

    def gets(
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: list[CheckResponse] | None = None,
    ) -> Callable[..., list[T]]:
        """Get list client."""
        return p.to_client(
            router=self.router,
            r2epm=router2get,
            f=f,
            convert=self.rettype.ofs,
            query=query,
            t_body=t_body,
            check_responses=check_responses,
        )

    def post(
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: list[CheckResponse] | None = None,
    ) -> Callable[..., T]:
        """Post client."""
        return p.to_client(
            router=self.router,
            r2epm=router2tpost,
            f=f,
            convert=self.rettype.of,
            query=query,
            t_body=t_body,
            check_responses=check_responses,
        )

    def put(
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: list[CheckResponse] | None = None,
    ) -> Callable[..., T]:
        """Put client."""
        return p.to_client(
            router=self.router,
            r2epm=router2put,
            f=f,
            convert=self.rettype.of,
            query=query,
            t_body=t_body,
            check_responses=check_responses,
        )

    def delete(
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: list[CheckResponse] | None = None,
    ) -> Callable[..., None]:
        """Delete client."""
        return p.to_client(
            router=self.router,
            r2epm=router2delete,
            f=f,
            convert=lambda _res: None,
            query=query,
            t_body=t_body,
            check_responses=check_responses,
        )

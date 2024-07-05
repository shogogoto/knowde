from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar

from fastapi import APIRouter  # noqa: TCH002
from pydantic import BaseModel

from knowde._feature._shared.api.endpoint import (
    router2delete,
    router2get,
    router2put,
    router2tpost,
)
from knowde._feature._shared.domain import APIReturn

if TYPE_CHECKING:

    from knowde._feature._shared.api.api_param import (
        APIQuery,
        BaseAPIPath,
        ComplexAPIQuery,
    )
    from knowde._feature._shared.api.types import CheckResponse

T = TypeVar("T", bound=APIReturn)


class ClientFactory(
    BaseModel,
    Generic[T],
    frozen=True,
    arbitrary_types_allowed=True,
):
    """to_clientをちょっと楽に."""

    router: APIRouter
    rettype: type[T]

    def get(  # noqa: PLR0913
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: Optional[list[CheckResponse]] = None,
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

    def gets(  # noqa: PLR0913
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: Optional[list[CheckResponse]] = None,
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

    def post(  # noqa: PLR0913
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: Optional[list[CheckResponse]] = None,
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

    def put(  # noqa: PLR0913
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: Optional[list[CheckResponse]] = None,
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

    def delete(  # noqa: PLR0913
        self,
        p: BaseAPIPath,
        f: Callable,
        query: APIQuery | ComplexAPIQuery | None = None,
        t_body: type[BaseModel] | None = None,
        check_responses: Optional[list[CheckResponse]] = None,
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

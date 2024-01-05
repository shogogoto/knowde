from typing import Callable
from uuid import UUID

from fastapi import APIRouter
from pydantic import Field
from starlette.status import HTTP_204_NO_CONTENT
from typing_extensions import override

from knowde._feature._shared.api.param import ApiParam


class DeleteParam(ApiParam, frozen=True):
    uid: UUID

    @classmethod
    @override
    def api_impl(
        cls,
        router: APIRouter,
        func: Callable,
    ) -> None:
        router.delete(
            "/{uid}",
            status_code=HTTP_204_NO_CONTENT,
            response_model=None,
        )(func)


class CompleteParam(ApiParam, frozen=True):
    pref_uid: str = Field(
        min_length=1,
        description="uuidと前方一致で検索",
    )

    @classmethod
    @override
    def api_impl(
        cls,
        router: APIRouter,
        func: Callable,
    ) -> None:
        router.get("/completion")(func)


class ListParam(ApiParam, frozen=True):
    @classmethod
    @override
    def api_impl(
        cls,
        router: APIRouter,
        func: Callable,
    ) -> None:
        router.get("")(func)

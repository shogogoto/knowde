from typing import Callable, ClassVar
from uuid import UUID

from fastapi import APIRouter
from pydantic import Field
from starlette.status import HTTP_204_NO_CONTENT
from typing_extensions import override

from knowde._feature._shared.api.param import ApiParam, HttpMethodParams


class RemoveParam(ApiParam, frozen=True):
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

    @classmethod
    @override
    def for_method(cls, **kwargs) -> HttpMethodParams:  # noqa: ANN003
        self = cls.model_validate(kwargs)
        return {
            "relative": self.uid.hex,
            "json": None,
            "params": None,
        }


class CompleteParam(ApiParam, frozen=True):
    relative: ClassVar[str] = "/relative"
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
        router.get(cls.relative)(func)

    @classmethod
    @override
    def for_method(cls, **kwargs) -> HttpMethodParams:  # noqa: ANN003
        self = cls.model_validate(kwargs)
        return {
            "relative": cls.relative,
            "json": None,
            "params": self.model_dump(),
        }


class ListParam(ApiParam, frozen=True):
    @classmethod
    @override
    def api_impl(
        cls,
        router: APIRouter,
        func: Callable,
    ) -> None:
        router.get("")(func)

    @classmethod
    @override
    def for_method(cls, **kwargs) -> HttpMethodParams:  # noqa: ANN003
        return {
            "relative": None,
            "json": None,
            "params": kwargs,
        }

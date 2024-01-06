from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar

from pydantic import BaseModel
from starlette.status import HTTP_200_OK

from knowde._feature._shared.cli.each_args.domain import EachArgsWrapper
from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature._shared.api.param import ApiParam
    from knowde._feature._shared.cli.to_request import HttpMethod
    from knowde._feature._shared.endpoint import Endpoint


T = TypeVar("T", bound=DomainModel)


class CliRequestError(Exception):
    pass


class CliRequest(BaseModel, Generic[T], frozen=True):
    endpoint: Endpoint
    M: type[T]  # DomainModel

    def method(
        self,
        m: HttpMethod,
        param: type[ApiParam],
        post_func: Optional[Callable] = None,
    ) -> Callable:
        return m.request_func(
            ep=self.endpoint,
            param=param,
            post_func=post_func,
            return_converter=lambda res: self.M.model_validate(res.json()),
        )

    def noreturn_method(
        self,
        m: HttpMethod,
        param: type[ApiParam],
        post_func: Optional[Callable] = None,
    ) -> Callable:
        return m.request_func(
            ep=self.endpoint,
            param=param,
            post_func=post_func,
            return_converter=lambda _res: None,
        )

    def ls_method(
        self,
        m: HttpMethod,
        param: type[ApiParam],
        post_func: Optional[Callable] = None,
    ) -> Callable:
        return m.request_func(
            ep=self.endpoint,
            param=param,
            post_func=post_func,
            return_converter=lambda res: [self.M.model_validate(e) for e in res.json()],
        )

    def ls(self) -> list[T]:
        res = self.endpoint.get()
        return [self.M.model_validate(e) for e in res.json()]

    def complete(self, pref_uid: str) -> T:
        res = self.endpoint.get(f"completion?pref_uid={pref_uid}")
        if res.status_code != HTTP_200_OK:
            msg = res.json()["detail"]["message"]
            msg = f"[{res.status_code}]:{msg}"
            raise CliRequestError(msg)
        return self.M.model_validate(res.json())

    def rm(self, uid: UUID) -> None:
        self.endpoint.delete(uid.hex)

    def post(self, param: BaseModel) -> T:
        res = self.endpoint.post(json=param.model_dump())
        return self.M.model_validate(res.json())

    def put(self, uid: UUID, param: BaseModel) -> T:
        res = self.endpoint.put(uid.hex, json=param.model_dump())
        return self.M.model_validate(res.json())

    def each_complete(self, arg_name: str) -> EachArgsWrapper:
        return EachArgsWrapper(
            converter=lambda pref_uid: self.complete(pref_uid).valid_uid,
            arg_name=arg_name,
        )

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel
from starlette.status import HTTP_200_OK

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature._shared.endpoint import Endpoint


T = TypeVar("T", bound=DomainModel)


class CliRequestError(Exception):
    pass


class CliRequest(BaseModel, Generic[T], frozen=True):
    endpoint: Endpoint
    M: type[T]  # DomainModel

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

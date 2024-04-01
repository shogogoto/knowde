from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, Field, RootModel, field_validator

from .errors import NotExistsUidAccessError

if TYPE_CHECKING:
    from requests import Response

    from knowde._feature._shared.repo import LBase

TZ = timezone(timedelta(hours=9), "Asia/Tokyo")


def jst_now() -> datetime:
    return datetime.now(tz=TZ)


class APIReturn(BaseModel, frozen=True):
    @classmethod
    def of(cls, res: Response) -> Self:
        return cls.model_validate(res.json())

    @classmethod
    def ofs(cls, res: Response) -> list[Self]:
        return [cls.model_validate(d) for d in res.json()]


class DomainModel(APIReturn, frozen=True):
    uid: UUID | None = None
    created: datetime | None = Field(None, repr=False)
    updated: datetime | None = Field(None, repr=False)

    @field_validator("created")
    def validate_created(cls, v: datetime) -> datetime:
        """Jst."""
        return v.astimezone(TZ)

    @field_validator("updated")
    def validate_updated(cls, v: datetime) -> datetime:
        """Jst."""
        return v.astimezone(TZ)

    @property
    def valid_uid(self) -> UUID:
        """Exists in db."""
        if self.uid is None:
            raise NotExistsUidAccessError
        return self.uid

    @classmethod
    def to_model(cls, lb: LBase) -> Self:
        return cls.model_validate(lb.__properties__)

    @classmethod
    def to_models(cls, lbs: list[LBase]) -> list[Self]:
        return [cls.to_model(lb) for lb in lbs]


M = TypeVar("M", bound=DomainModel)


class ModelList(RootModel[list[M]], frozen=True):
    def attrs(self, key: str) -> list[Any]:
        return [getattr(m, key) for m in self.root]

    def first(self, key: str, value: Any) -> M:  # noqa: ANN401
        return next(
            filter(
                lambda x: getattr(x, key) == value,
                self.root,
            ),
        )


T = TypeVar("T", bound=BaseModel)


class Composite(BaseModel, Generic[T], frozen=True):
    parent: T
    children: list[Composite[T]] = Field(default_factory=list)

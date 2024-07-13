from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import TYPE_CHECKING, Optional, Self, TypeVar
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, Field, field_validator

from knowde._feature._shared.errors.domain import NotExistsAccessError
from knowde._feature._shared.timeutil import TZ

if TYPE_CHECKING:
    from requests import Response

    from knowde._feature._shared.repo import LBase
    from knowde._feature._shared.types import NeoModel


class APIReturn(BaseModel, frozen=True):
    @classmethod
    def of(cls, res: Response) -> Self:
        return cls.model_validate(res.json())

    @classmethod
    def ofs(cls, res: Response) -> list[Self]:
        return [cls.model_validate(d) for d in res.json()]


T = TypeVar("T", bound=BaseModel)


def neolabel2model(t: type[T], lb: NeoModel, attrs: Optional[dict] = None) -> T:
    if attrs is None:
        attrs = {}
    return t.model_validate({**lb.__properties__, **attrs})


class Entity(APIReturn, frozen=True):
    """永続化対象."""

    uid: UUID | None = None
    created: datetime = Field(repr=False)
    updated: datetime = Field(repr=False)

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
            raise NotExistsAccessError
        return self.uid

    @classmethod
    def to_model(cls, lb: LBase, attrs: Optional[dict] = None) -> Self:
        return neolabel2model(cls, lb, attrs)

    @classmethod
    def to_models(cls, lbs: list[LBase]) -> list[Self]:
        return [cls.to_model(lb) for lb in lbs]

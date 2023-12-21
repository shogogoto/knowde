from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import TYPE_CHECKING, Any, Self, TypeVar
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, RootModel, field_validator

from .errors import NotExistsUidAccessError
from .timeutil import TZ

if TYPE_CHECKING:
    from knowde._feature._shared.repo.label import LBase


class DomainModel(BaseModel, frozen=True):
    uid: UUID | None = None
    created: datetime | None = None
    updated: datetime | None = None

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
    def to_models(cls, lbs: LBase) -> list[Self]:
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

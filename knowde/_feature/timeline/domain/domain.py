from __future__ import annotations

from pydantic import BaseModel, Field

from knowde._feature._shared.domain import Entity
from knowde._feature._shared.errors.domain import NotExistsAccessError


class TimelineRoot(Entity, frozen=True):
    """時系列ルート."""

    name: str


class Year(Entity, frozen=True):
    value: int


class Month(Entity, frozen=True):
    value: int = Field(ge=1, le=12)


class Day(Entity, frozen=True):
    value: int = Field(ge=1, le=31)


class TimeValue(BaseModel, frozen=True):
    name: str
    year: int
    month: int | None = Field(None, ge=1, le=12, init_var=False)
    day: int | None = Field(None, ge=1, le=31, init_var=False)


class Time(BaseModel, frozen=True):
    """日付."""

    tl: TimelineRoot
    y: Year
    m: Month | None = None
    d: Day | None = None

    @property
    def value(self) -> TimeValue:
        return TimeValue(
            name=self.tl.name,
            year=self.y.value,
            month=self.m.value if self.m is not None else None,
            day=self.d.value if self.d is not None else None,
        )

    @property
    def day(self) -> Day:
        if self.d is None:
            raise NotExistsAccessError
        return self.d

    @property
    def month(self) -> Month:
        if self.m is None:
            raise NotExistsAccessError
        return self.m


class Days(BaseModel, frozen=True):
    times: list[Time]

from __future__ import annotations

from pydantic import BaseModel, Field

from knowde._feature._shared.domain import Entity


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
    """時刻."""

    tl: TimelineRoot
    year: Year
    month: Month | None = None
    day: Day | None = None

    @property
    def value(self) -> TimeValue:
        return TimeValue(
            name=self.tl.name,
            year=self.year.value,
            month=self.month.value if self.month is not None else None,
            day=self.day.value if self.day is not None else None,
        )

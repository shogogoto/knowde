from __future__ import annotations

from typing import Self

from pydantic import BaseModel, Field

from knowde._feature._shared.domain import Entity
from knowde._feature._shared.domain.domain import APIReturn
from knowde._feature._shared.errors.domain import NotExistsAccessError
from knowde._feature._shared.types import NXGraph  # noqa: TCH001


class TimelineRoot(Entity, frozen=True):
    """時系列ルート."""

    name: str


class Year(Entity, frozen=True):
    value: int


class Month(Entity, frozen=True):
    value: int = Field(ge=1, le=12)


class Day(Entity, frozen=True):
    value: int = Field(ge=1, le=31)


class TimeValue(APIReturn, frozen=True):
    name: str
    year: int | None = Field(default=None, init_var=False)
    month: int | None = Field(default=None, ge=1, le=12, init_var=False)
    day: int | None = Field(default=None, ge=1, le=31, init_var=False)

    @property
    def tuple(self) -> tuple[str, int | None, int | None, int | None]:
        return (self.name, self.year, self.month, self.day)

    def __lt__(self, other: Self) -> bool:
        return self.tuple < other.tuple


class Time(BaseModel, frozen=True):
    """日付."""

    tl: TimelineRoot
    y: Year | None = None
    m: Month | None = None
    d: Day | None = None

    def __lt__(self, other: Self) -> bool:
        return self.value.tuple < other.value.tuple

    @property
    def value(self) -> TimeValue:
        return TimeValue(
            name=self.tl.name,
            year=self.y.value if self.y is not None else None,
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

    @property
    def year(self) -> Year:
        if self.y is None:
            raise NotExistsAccessError
        return self.y

    @property
    def tail(self) -> TimelineRoot | Year | Month | Day:
        ts = [self.tl, self.y, self.m, self.d]
        return [t for t in ts if t is not None][-1]


class Timeline(BaseModel, frozen=True):
    g: NXGraph
    root: TimelineRoot

    @property
    def times(self) -> list[Time]:
        """直積."""
        if len(self.g.nodes) == 0:
            return [Time(tl=self.root)]
        times = []
        ys = self.g[self.root]
        for y in ys:
            ms = self.g[y]
            if len(ms) == 0:
                times.append(Time(tl=self.root, y=y))
            for m in ms:
                ds = self.g[m]
                if len(ds) == 0:
                    times.append(Time(tl=self.root, y=y, m=m))
                times.extend([Time(tl=self.root, y=y, m=m, d=d) for d in ds])
        return times

    @property
    def values(self) -> list[TimeValue]:
        return [t.value for t in self.times]

"""時系列domain."""
from __future__ import annotations

from typing import Optional, Self

from pydantic import BaseModel, Field, model_validator

from knowde.primitive.__core__.domain import Entity
from knowde.primitive.__core__.domain.domain import APIReturn
from knowde.primitive.__core__.errors.domain import NotExistsAccessError
from knowde.primitive.__core__.types import NXGraph

from .errors import InvalidTimeYMDError


class TimelineRoot(Entity, frozen=True):
    """時系列ルート."""

    name: str = Field(min_length=1)


class YMD(Entity, frozen=True):
    """年月日共通."""

    value: int


class Year(YMD, frozen=True):
    """年."""


class Month(YMD, frozen=True):
    """月."""

    value: int = Field(ge=1, le=12)


class Day(YMD, frozen=True):
    """日."""

    value: int = Field(ge=1, le=31)


def validate_ymd(
    y: int | Year | None,
    m: int | Month | None,
    d: int | Day | None,
) -> None:
    """YMDの組の妥当性チェック."""
    if y is not None:
        if m is None and d is not None:
            msg = "年日があるのに月ない"
            raise InvalidTimeYMDError(msg)
    elif m is not None or d is not None:
        msg = "年がないのに月日あり"
        raise InvalidTimeYMDError(msg)


class TimeValue(APIReturn, frozen=True):
    """UUIDなし時間."""

    name: str
    year: int | None = Field(default=None, init_var=False)
    month: int | None = Field(default=None, ge=1, le=12, init_var=False)
    day: int | None = Field(default=None, ge=1, le=31, init_var=False)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        validate_ymd(*self.tuple[1:])
        return self

    @classmethod
    def new(
        cls,
        name: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ) -> Self:
        """instantiate."""
        return cls(name=name, year=year, month=month, day=day)

    @property
    def tuple(self) -> tuple[str, int | None, int | None, int | None]:
        """intタプル."""
        return (self.name, self.year, self.month, self.day)

    @property
    def ymd_tuple(self) -> tuple[int | None, int | None, int | None]:
        """時系列名なしintタプル."""
        return self.tuple[1:]

    def __lt__(self, other: Self) -> bool:
        """比較."""
        return self.tuple < other.tuple


class Time(BaseModel, frozen=True):
    """日付."""

    tl: TimelineRoot
    y: Year | None = None
    m: Month | None = None
    d: Day | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        validate_ymd(self.y, self.m, self.d)
        return self

    def __lt__(self, other: Self) -> bool:
        """比較."""
        return self.value.tuple < other.value.tuple

    @property
    def value(self) -> TimeValue:
        """UUIDなしへ変換."""
        return TimeValue(
            name=self.tl.name,
            year=self.y.value if self.y is not None else None,
            month=self.m.value if self.m is not None else None,
            day=self.d.value if self.d is not None else None,
        )

    @property
    def day(self) -> Day:  # noqa: D102
        if self.d is None:
            raise NotExistsAccessError
        return self.d

    @property
    def month(self) -> Month:  # noqa: D102
        if self.m is None:
            raise NotExistsAccessError
        return self.m

    @property
    def year(self) -> Year:  # noqa: D102
        if self.y is None:
            raise NotExistsAccessError
        return self.y

    @property
    def leaf(self) -> YMD:
        """より細かい時刻を返す."""
        ts = [self.tl, self.y, self.m, self.d]
        ret = [t for t in ts if t is not None][-1]
        if isinstance(ret, TimelineRoot):
            msg = "年がありません"
            raise TypeError(msg)
        return ret

    def only_tl(self) -> bool:
        """時系列名しかないか否か."""
        return self.y is None and self.m is None and self.d is None


class Timeline(BaseModel, frozen=True):
    """時系列グラフ."""

    root: TimelineRoot
    g: NXGraph

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
        """UUIDなしへ."""
        return [t.value for t in self.times]

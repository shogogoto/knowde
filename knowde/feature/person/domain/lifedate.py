"""人生日付."""
from __future__ import annotations

from typing import Optional, Self

from pydantic import BaseModel, Field, model_validator

from knowde._feature._shared.errors.errors import DomainError
from knowde._feature.timeline.domain.const import SOCIETY_TIMELINE
from knowde._feature.timeline.domain.domain import Time, TimeValue


class LifeDateInvalidError(DomainError):
    """不正な人生日付."""

    msg = "月が不明なのに日が分かるなどを許さない."


class DeathBeforeBirthError(DomainError):
    """生まれる前に死ぬ."""


class LifeDate(BaseModel, frozen=True):
    """誕生日や命日を扱う.

    何月何日までの細かい値が分からなくてもいいようにしたい
    """

    year: int = Field()  # BCはマイナスになるので負の値も許容
    month: int | None = Field(default=None, ge=1, le=12, init_var=False)
    day: int | None = Field(default=None, ge=1, le=31, init_var=False)

    @property
    def value(self) -> TimeValue:
        """To TimeValue."""
        return TimeValue(
            name=SOCIETY_TIMELINE,
            year=self.year,
            month=self.month,
            day=self.day,
        )

    @classmethod
    def from_time(cls, t: Time) -> Self:
        """From time factory."""
        return cls(
            year=t.year.value,
            month=t.m.value if t.m is not None else None,
            day=t.d.value if t.d is not None else None,
        )

    @classmethod
    def new(cls, year: int, month: int | None = None, day: int | None = None) -> Self:
        """keyword指定メンドイから."""
        return cls(year=year, month=month, day=day)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.month is None and self.day is not None:
            raise LifeDateInvalidError
        return self

    def to_str(self) -> str:
        """文字列化."""
        y = str(self.year)
        return "".join([y, to_str(self.month), to_str(self.day)])

    @classmethod
    def from_str(cls, v: str | None) -> Self | None:
        """文字列からinstantiate."""
        if v is None:
            return None
        i_last = len(v)
        i2 = i_last - 2
        i1 = i2 - 2
        d = to_int(v[i2:i_last])
        m = to_int(v[i1:i2])
        y = to_int(v[0:i1])
        if y is None:
            raise LifeDateInvalidError
        return cls(year=y, month=m, day=d)

    @property
    def tuple(self) -> tuple[int, int | None, int | None]:
        """To tuple."""
        return (self.year, self.month, self.day)


NULL_EXPRESSION = "99"


def to_str(v: int | None) -> str:
    """人生日付int to str."""
    if v is None:
        return NULL_EXPRESSION
    return str(v).zfill(2)


def to_int(v: str | None) -> int | None:
    """人生日付文字列 to int."""
    if v == NULL_EXPRESSION or v is None:
        return None
    return int(v)


def t_society(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> TimeValue:
    """Util."""
    return TimeValue.new(SOCIETY_TIMELINE, year, month, day)


class LifeSpan(BaseModel, frozen=True):
    """人生."""

    birth: LifeDate | None = None
    death: LifeDate | None = None

    @classmethod
    def from_times(cls, t_birth: Time, t_death: Time) -> Self:
        """From times factory."""
        b = None if t_birth.only_tl() else LifeDate.from_time(t_birth)
        d = None if t_death.only_tl() else LifeDate.from_time(t_death)
        return cls(birth=b, death=d)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if (
            self.birth is not None
            and self.death is not None
            and self.death.value < self.birth.value
        ):
            raise DeathBeforeBirthError
        return self

    def to_str(self) -> str:
        """To str."""
        b = "" if self.birth is None else self.birth.to_str()
        d = "" if self.death is None else self.death.to_str()
        if b == d == "":
            return ""
        return f"{b} ~ {d}"

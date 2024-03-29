from __future__ import annotations

from typing import Self

from pydantic import BaseModel, Field, model_validator
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.domain import DomainModel
from knowde._feature.person.errors import LifeDateInvalidError


class LifeDate(BaseModel, frozen=True):
    """誕生日や命日を扱う.

    何月何日までの細かい値が分からなくてもいいようにしたい
    """

    year: int = Field()  # BCはマイナスになるので負の値も許容
    month: int | None = Field(None, ge=1, le=12)
    day: int | None = Field(None, ge=1, le=31)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.month is None and self.day is not None:
            raise LifeDateInvalidError
        return self

    def to_str(self) -> str:
        y = str(self.year)
        return "".join([y, to_str(self.month), to_str(self.day)])

    @classmethod
    def from_str(cls, v: str) -> Self:
        i_last = len(v)
        i2 = i_last - 2
        i1 = i2 - 2
        d = to_int(v[i2:i_last])
        m = to_int(v[i1:i2])
        y = to_int(v[0:i1])
        if y is None:
            raise LifeDateInvalidError
        return cls(year=y, month=m, day=d)


class AuthorParam(BaseModel, frozen=True):
    name: str
    # 別フィーチャーに分離するかも
    birth: LifeDate | None = Field(default=None, title="誕生日")
    death: LifeDate | None = Field(default=None, title="命日")


OptionalAuthorParam = create_partial_model(AuthorParam)


class Author(DomainModel, frozen=True):
    name: str
    # 別フィーチャーに分離するかも
    birth: str | None
    death: str | None


NULL_EXPRESSION = "99"


def to_str(v: int | None) -> str:
    if v is None:
        return NULL_EXPRESSION
    return str(v).zfill(2)


def to_int(v: str) -> int | None:
    if v == NULL_EXPRESSION:
        return None
    return int(v)

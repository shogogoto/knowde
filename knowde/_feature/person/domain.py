from __future__ import annotations

from typing import Self

from pydantic import BaseModel, Field, model_validator

from knowde._feature._shared.domain import DomainModel
from knowde._feature.person.errors import UnclearLifeDateError


class AuthorParam(BaseModel, frozen=True):
    name: str
    # 別フィーチャーに分離するかも
    birth: LifeDate | None = Field(None, title="誕生日")
    death: LifeDate | None = Field(None, title="命日")


class Author(DomainModel, AuthorParam, frozen=True):
    pass


def to_str(v: int | None) -> str:
    if v is None:
        return "99"
    return str(v).zfill(2)


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
            raise UnclearLifeDateError
        return self

    def to_str(self) -> str:
        y = str(self.year)
        return "".join([y, to_str(self.month), to_str(self.day)])

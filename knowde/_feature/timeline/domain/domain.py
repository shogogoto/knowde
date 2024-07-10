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


class Time(BaseModel, frozen=True):
    """時刻."""

    name: str
    year: int
    month: int | None = Field(None, ge=1, le=12, init=False)

    day: int | None = Field(None, ge=1, le=31, init=False)

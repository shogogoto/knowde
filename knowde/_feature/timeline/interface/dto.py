from __future__ import annotations

from pydantic import BaseModel, Field


class TimelineAddParam(BaseModel, frozen=True):
    name: str = Field(description="時系列名")
    year: int | None = Field(default=None, description="年")
    month: int | None = Field(default=None, description="月")
    day: int | None = Field(default=None, description="日")


class TimelineListRemoveParam(BaseModel, frozen=True):
    name: str = Field(description="時系列名")
    year: int | None = Field(default=None, description="年")
    month: int | None = Field(default=None, description="月")

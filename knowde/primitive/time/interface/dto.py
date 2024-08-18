"""data transfer object."""
from __future__ import annotations

from pydantic import BaseModel, Field

from knowde.primitive.time.domain.timestr import TS_PT


class TimelineParam(BaseModel, frozen=True):
    """interface用."""

    name: str = Field(description="時系列名")
    year: int | None = Field(default=None, description="年")
    month: int | None = Field(default=None, description="月")
    day: int | None = Field(default=None, description="日")


class TimeStrParam(BaseModel, frozen=True):
    """interface用."""

    timestr: str = Field(pattern=TS_PT, description="yyyy[/MM[/dd]][@name]")

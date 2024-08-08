from __future__ import annotations

from pydantic import BaseModel, Field

from knowde._feature.timeline.domain.timestr import TS_PT


class TimelineParam(BaseModel, frozen=True):
    name: str = Field(description="時系列名")
    year: int | None = Field(default=None, description="年")
    month: int | None = Field(default=None, description="月")
    day: int | None = Field(default=None, description="日")


class TimeStrParam(BaseModel, frozen=True):
    timestr: str = Field(pattern=TS_PT, description="yyyy[/MM[/dd]][@name]")


class TimelineCLIParam(BaseModel, frozen=True):
    pass

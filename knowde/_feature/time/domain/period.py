from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, model_validator

from knowde._feature.time.domain.const import SOCIETY_TIMELINE
from knowde._feature.time.domain.domain import TimeValue  # noqa: TCH001
from knowde._feature.time.domain.errors import (
    EndBeforeStartError,
    NotEqualTimelineError,
)
from knowde._feature.time.domain.timestr import TimeStr

if TYPE_CHECKING:
    from knowde._feature.time.domain.domain import Time


class Period(BaseModel, frozen=True):
    """期間."""

    start: TimeValue | None = None
    end: TimeValue | None = None

    @classmethod
    def from_times(cls, start: Time, end: Time) -> Self:
        return cls(
            start=None if start.only_tl() else start.value,
            end=None if end.only_tl() else end.value,
        )

    @classmethod
    def from_strs(cls, s_str: str | None = None, e_str: str | None = None) -> Self:
        s = TimeStr(value=s_str).val if s_str is not None else None
        e = TimeStr(value=e_str).val if e_str is not None else None
        return cls(start=s, end=e)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.start is not None and self.end is not None:
            if self.end < self.start:
                raise EndBeforeStartError
            if self.start.name != self.end.name:
                raise NotEqualTimelineError
        return self

    @property
    def name(self) -> str:
        """時系列名."""
        if self.start is not None:
            return self.start.name
        if self.end is not None:
            return self.end.name
        return SOCIETY_TIMELINE

    @property
    def output(self) -> str:
        """Output for cli."""
        s = TimeStr.from_val(self.start).without_name if self.start is not None else ""
        e = TimeStr.from_val(self.end).without_name if self.end is not None else ""
        return f"{self.name}:{s}~{e}"

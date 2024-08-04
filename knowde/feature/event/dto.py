"""event DTO."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, Field

from knowde.feature.person.domain.lifedate import SOCIETY_TIMELINE


class AddEventParam(BaseModel, frozen=True):
    """イベント追加パラメータ."""

    text: str = Field(description="説明")
    location_uid: UUID | None = Field(default=None, description="場所のUUID")
    time_uid: UUID | None = Field(default=None, description="時刻のUUID")
    timename: str = Field(default=SOCIETY_TIMELINE, description="時系列名")


# class AddEventCLIParam(BaseModel, frozen=True):
#     pass


class ChangeTextParam(BaseModel, frozen=True):
    """イベント変更パラメータ."""

    text: str = Field(description="説明")

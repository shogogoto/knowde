"""認可の種類."""

import uuid
from datetime import datetime

from fastapi_users import schemas
from pydantic import BaseModel, Field


class UserCreate(schemas.BaseUserCreate):
    """作成."""


LEN_DISPLAY_NAME = 32
LEN_PROFILE = 160  # twitterと同じらしい


class CommonSchema(BaseModel):  # noqa: D101
    display_name: str | None = Field(default=None, max_length=LEN_DISPLAY_NAME)
    avatar_url: str | None = None
    profile: str | None = Field(default=None, max_length=LEN_PROFILE)


class UserRead(CommonSchema, schemas.BaseUser[uuid.UUID]):
    """読み取り."""

    created: datetime


class UserUpdate(CommonSchema, schemas.BaseUserUpdate):
    """更新."""

"""認可の種類."""

import uuid

from fastapi_users import schemas
from pydantic import BaseModel


class CommonSchema(BaseModel):  # noqa: D101
    display_name: str | None = None


class UserRead(CommonSchema, schemas.BaseUser[uuid.UUID]):
    """読み取り."""


class UserCreate(CommonSchema, schemas.BaseUserCreate):
    """作成."""


class UserUpdate(CommonSchema, schemas.BaseUserUpdate):
    """更新."""

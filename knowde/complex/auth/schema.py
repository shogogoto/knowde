"""認可の種類."""

import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """読み取り."""


class UserCreate(schemas.BaseUserCreate):
    """作成."""


class UserUpdate(schemas.BaseUserUpdate):
    """更新."""

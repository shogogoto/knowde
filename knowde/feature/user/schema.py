"""認可の種類."""

from datetime import datetime
from typing import Self

from fastapi_users import schemas

from knowde.feature.user import CommonSchema
from knowde.shared.user.label import LUser


class UserCreate(schemas.BaseUserCreate):
    """作成."""


class UserReadPublic(CommonSchema):
    """公開ユーザー情報."""

    created: datetime


class UserRead(UserReadPublic, schemas.BaseUser[str]):
    """読み取り."""

    @classmethod
    def from_label(cls, lb: LUser) -> Self:  # noqa: D102
        return cls(
            id=lb.uid,
            email=lb.email,
            is_active=lb.is_active,
            is_verified=lb.is_verified,
            is_superuser=lb.is_superuser,
            created=lb.created,
            display_name=lb.display_name,
            profile=lb.profile,
            avatar_url=lb.avatar_url,
            username=lb.username,
        )


class UserUpdate(CommonSchema, schemas.BaseUserUpdate):
    """更新."""

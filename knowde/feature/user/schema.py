"""認可の種類."""

from datetime import datetime
from typing import Self

from fastapi_users import schemas

from knowde.feature.user import CommonSchema
from knowde.shared.labels.user import LUser


class UserCreate(schemas.BaseUserCreate):
    """作成."""


class UserRead(CommonSchema, schemas.BaseUser[str]):
    """読み取り."""

    created: datetime

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
        )


class UserUpdate(CommonSchema, schemas.BaseUserUpdate):
    """更新."""

    id: str | None = None

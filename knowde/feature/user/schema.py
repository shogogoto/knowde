"""認可の種類."""

from typing import Self
from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, Field
from pydantic_partial import create_partial_model

from knowde.shared.user.label import LUser
from knowde.shared.user.schema import CommonSchema, UserReadPublic


class SecurityFields(BaseModel):
    """パスワードなどの共通設定."""

    password: str = Field(
        default=...,
        min_length=3,  # fastapi-users minが3となっていたのでそれに合わせる
        max_length=100,
        title="パスワード",
        description="3文字以上100文字以内で入力してください",
    )


class UserCreate(SecurityFields, schemas.BaseUserCreate):
    """作成."""


class UserRead(UserReadPublic, schemas.BaseUser[UUID]):
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


class UserUpdate(
    create_partial_model(SecurityFields),
    CommonSchema,
    schemas.BaseUserUpdate,
):
    """更新."""

"""ユーザーがシステムにアクセスするための一連の認証情報や権限.

アカウントは、ユーザーに特定の役割や権限を付与するために使用される

follow機能
"""
from __future__ import annotations

from uuid import UUID

from pydantic import EmailStr, Field

from knowde.primitive.__core__.neoutil import BaseMapper

from .repo import LAccount, LUser


class User(BaseMapper):
    """UserProtocol[UUID]を満たす."""

    __label__ = LUser
    uid: UUID | None = None
    email: EmailStr
    hashed_password: str
    is_active: bool
    is_superuser: bool = False
    is_verified: bool = False
    oauth_accounts: list[Account] = Field(default_factory=list)

    @property
    def id(self) -> UUID:  # noqa: D102
        if self.uid is None:
            raise
        return self.uid


class Account(BaseMapper):
    """OAuthAccountProtocol[UUID]を満たす."""

    __label__ = LAccount
    oauth_name: str
    access_token: str
    expires_at: int | None = None
    refresh_token: str | None = None
    account_id: str
    account_email: EmailStr

    @property
    def id(self) -> str:  # noqa: D102
        return self.account_id

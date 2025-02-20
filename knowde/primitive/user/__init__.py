"""ユーザーがシステムにアクセスするための一連の認証情報や権限.

アカウントは、ユーザーに特定の役割や権限を付与するために使用される


Google で SSO
普通にUserでSign up.


User
  name for display  SSOではemailの@の前にしとくか
  email optional
  uid
  password optional passwordはuserではなく認証のドメイン
  created

だけあればいい
認証で必要な情報を持つのはAccountと呼び分ける

SysNetの所有者としてはOwnerと呼んだり

"""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from pydantic import EmailStr, Field

from knowde.primitive.__core__.neoutil import BaseMapper

from .repo import LAccount, LUser


class User(BaseMapper):
    """UserProtocol[UUID]を満たす."""

    __label__ = LUser
    uid: UUID
    email: EmailStr
    hashed_password: str
    is_active: bool
    is_superuser: bool = False
    is_verified: bool = False
    oauth_accounts: list[Account] = Field(default_factory=list)

    @property
    def id(self) -> UUID:  # noqa: D102
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

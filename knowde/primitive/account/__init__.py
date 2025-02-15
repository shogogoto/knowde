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

from typing import Self
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel

from knowde.primitive.__core__.domain.domain import neolabel2model
from knowde.primitive.account.repo import LAccount, LSSOAccount


class Account(BaseModel):
    """UserProtocol[UUID]を満たす."""

    uid: UUID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool = False
    is_verified: bool = False

    @property
    def id(self) -> UUID:  # noqa: D102
        return self.uid

    @classmethod
    def from_lb(cls, lb: LAccount) -> Self:
        """Neomodel label to model."""
        return neolabel2model(cls, lb)

    def tolabel(self) -> LAccount:
        """Model to neomodel label."""
        return LAccount(**self.model_dump())


class SSOAccount(BaseModel):
    """OAuthAccountProtocol[UUID]を満たす."""

    uid: UUID
    oauth_name: str
    access_token: str
    expires_at: int | None = None
    refresh_token: str | None = None
    account_id: str
    account_email: str

    @property
    def id(self) -> UUID:  # noqa: D102
        return self.uid

    @classmethod
    def from_lb(cls, lb: LSSOAccount) -> Self:  # noqa: D102
        return neolabel2model(cls, lb)

    def tolabel(self) -> LSSOAccount:  # noqa: D102
        return LSSOAccount(**self.model_dump())


class AccountWithSSO(BaseModel):
    """User protocol including a list of OAuth accounts."""

    uid: UUID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    oauth_accounts: list[SSOAccount]

    @property
    def id(self) -> UUID:  # noqa: D102
        return self.uid

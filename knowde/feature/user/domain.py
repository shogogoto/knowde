"""ユーザーがシステムにアクセスするための一連の認証情報や権限.

アカウントは、ユーザーに特定の役割や権限を付与するために使用される
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi_users.schemas import BaseOAuthAccount, BaseOAuthAccountMixin
from pydantic import BeforeValidator, EmailStr

from knowde.feature.user.schema import CommonSchema
from knowde.shared.util import neo4j_dt_validator


class User(CommonSchema, BaseOAuthAccountMixin):
    """UserProtocol[UUID]を満たす."""

    uid: UUID | None = None
    email: EmailStr
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created: Annotated[datetime, BeforeValidator(neo4j_dt_validator)]

    @property
    def id(self) -> str:  # noqa: D102
        if self.uid is None:
            msg = "uid is None"
            raise ValueError(msg)
        if isinstance(self.uid, UUID):
            return self.uid.hex
        return str(self.uid)


class Account(BaseOAuthAccount):
    """OAuthAccountProtocol[UUID]を満たす."""

    account_email: EmailStr

    @property
    def id(self) -> str:  # noqa: D102
        return self.account_id

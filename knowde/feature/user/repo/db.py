"""user CRUD on fastapi-users."""

from __future__ import annotations

from typing import override
from uuid import UUID

from fastapi_users.db import (
    BaseUserDatabase,
)

from knowde.feature.user.domain import User
from knowde.feature.user.oauth.label import LAccount
from knowde.shared.types.mapper import label2model
from knowde.shared.user.label import LUser


class AccountDB(BaseUserDatabase[User, UUID]):
    """DB adapter for fastapi-users."""

    @override
    async def get(self, id):
        # print("---------get")
        lb = await LUser.nodes.get_or_none(uid=id.hex)
        if lb is None:
            return None
        return label2model(User, lb)

    @override
    async def get_by_email(self, email):
        # print("---------get by email")
        lb = await LUser.nodes.get_or_none(email=email)
        if lb is None:
            return None
        return label2model(User, lb)

    @override
    async def get_by_oauth_account(self, oauth, account_id):
        la = await LAccount.nodes.get_or_none(account_id=account_id)
        if la is None:
            return None
        lu = await la.user.single()
        return label2model(User, lu)

    @override
    async def create(self, create_dict):
        if await self.get_by_email(create_dict["email"]):
            raise  # noqa: PLE0704
        lb = await LUser(**create_dict).save()
        return label2model(User, lb)

    @override
    async def update(self, user, update_dict):
        lb = await LUser.nodes.get(uid=user.id)
        for k, v in update_dict.items():
            if v is None:
                continue
            setattr(lb, k, v)
        lb = await lb.save()
        return label2model(User, lb)

    @override
    async def delete(self, user):
        lb = await LUser.nodes.get(uid=user.id.hex)
        await lb.delete()

    # OAUTH
    @override
    async def add_oauth_account(self, user, create_dict):
        la = await LAccount(create_dict).save()
        lu = await LUser.nodes.get(uid=user.id.hex)
        await lu.accounts.connect(la)
        return user

    @override
    async def update_oauth_account(self, user, oauth_account, update_dict):
        return user

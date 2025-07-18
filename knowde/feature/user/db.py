"""user CRUD on fastapi-users."""

from __future__ import annotations

from typing import override
from uuid import UUID

from fastapi_users.db import (
    BaseUserDatabase,
)

from knowde.feature.user.domain import Account, User
from knowde.shared.user.label import LAccount, LUser


async def _get_user_with_account(**kwargs) -> User | None:
    lb: LUser = await LUser.nodes.get_or_none(**kwargs)
    if lb is None:
        return None
    accounts = [
        Account.model_validate(ac.__properties__) for ac in await lb.accounts.all()
    ]
    return User.model_validate({**lb.__properties__, "oauth_accounts": accounts})


class AccountDB(BaseUserDatabase[User, UUID]):
    """DB adapter for fastapi-users."""

    @override
    async def get(self, id):
        return await _get_user_with_account(uid=id.hex)

    @override
    async def get_by_email(self, email):
        return await _get_user_with_account(email=email)

    @override
    async def get_by_oauth_account(self, oauth, account_id):
        la: LAccount | None = await LAccount.nodes.get_or_none(account_id=account_id)
        if la is None:
            return None
        lu: LUser = await la.user.single()
        return User.model_validate(lu.__properties__)

    @override
    async def create(self, create_dict):
        if await self.get_by_email(create_dict["email"]):
            raise  # noqa: PLE0704
        lb = await LUser(**create_dict).save()
        return User.model_validate(lb.__properties__)

    @override
    async def update(self, user, update_dict):
        lb = await LUser.nodes.get(uid=user.id.hex)
        for k, v in update_dict.items():
            if v is None:
                continue
            setattr(lb, k, v)
        lb = await lb.save()
        return User.model_validate(lb.__properties__)

    @override
    async def delete(self, user):
        lb = await LUser.nodes.get(uid=user.id.hex)
        await lb.delete()

    # OAUTH BaseUserManager.oauth_callbackで使用される
    @override
    async def add_oauth_account(self, user, create_dict):
        la = await LAccount(**create_dict).save()
        lu: LUser = await LUser.nodes.get(uid=user.id.hex)
        await lu.accounts.connect(la)
        return user

    @override
    async def update_oauth_account(self, user, oauth_account, update_dict):
        la = LAccount.nodes.get(account_id=oauth_account.account_id)
        for k, v in update_dict.items():
            if v is None:
                continue
            setattr(la, k, v)
        la.save()
        return user

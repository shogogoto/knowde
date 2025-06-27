"""user CRUD on fastapi-users."""

from __future__ import annotations

from datetime import datetime
from typing import Any, override
from uuid import UUID

from fastapi_users.db import (
    BaseUserDatabase,
)

from knowde.feature.user.domain import Account, User
from knowde.feature.user.repo.label import LAccount
from knowde.shared.labels.user import LUser
from knowde.shared.types.mapper import label2model
from knowde.shared.util import TZ


class AccountDB(BaseUserDatabase[User, UUID]):
    """DB adapter for fastapi-users."""

    @override
    async def get(self, id: UUID) -> User | None:
        """Get a single user by id."""
        # print("---------get")
        lb = LUser.nodes.get_or_none(uid=id.hex)
        if lb is None:
            return None
        return label2model(User, lb)

    @override
    async def get_by_email(self, email: str) -> User | None:
        """Get a single user by email."""
        # print("---------get by email")
        lb = LUser.nodes.get_or_none(email=email)
        if lb is None:
            return None
        return label2model(User, lb)

        return User.get_or_none(email=email)

    @override
    async def get_by_oauth_account(
        self,
        oauth: str,
        account_id: str,
    ) -> User | None:
        """Get a single user by OAuth account id."""
        # print("---------get by oauth")
        la = LAccount.nodes.get_or_none(account_id=account_id)
        if la is None:
            return None
        lu = la.user.single()
        return label2model(User, lu)

    @override
    async def create(self, create_dict: dict[str, Any]) -> User:
        """Create a user."""
        if await self.get_by_email(create_dict["email"]):
            raise  # noqa: PLE0704
        lb = LUser(**create_dict).save()
        return label2model(User, lb)

    @override
    async def update(self, user: User, update_dict: dict) -> User:
        """Update a user."""
        # print("------------ update")
        lb = LUser.nodes.get(uid=user.id.hex)
        for key, value in update_dict.items():
            if value is None:
                continue
            setattr(lb, key, value)
        lb.created = datetime.now(tz=TZ)
        lb = lb.save()
        return label2model(User, lb)

    @override
    async def delete(self, user: User) -> None:
        """Delete a user."""
        # print("------------ delete")
        lb = LUser.nodes.get(uid=user.id.hex)
        lb.delete()

    # OAUTH
    @override
    async def add_oauth_account(
        self,
        user: User,
        create_dict: dict[str, Any],
    ) -> User:
        """Create an OAuth account and add it to the user."""
        # print("------------ add oauth account")
        account = Account.model_validate(create_dict)
        la = account.tolabel().save()
        lu = LUser.nodes.get(uid=user.id.hex)
        lu.accounts.connect(la)
        return user

    @override
    async def update_oauth_account(
        self,
        user: User,
        oauth_account: Account,
        update_dict: dict[str, Any],
    ) -> User:
        """Update an OAuth account on a user."""
        print("------------ update oauth account", user, update_dict)  # noqa: T201

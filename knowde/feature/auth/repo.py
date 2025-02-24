"""DB."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi_users.db import (
    BaseUserDatabase,
)

from knowde.primitive.user import Account, User
from knowde.primitive.user.repo import LAccount, LUser


class AccountDB(BaseUserDatabase[User, UUID]):
    """DB adapter for fastapi-users."""

    async def get(self, id: UUID) -> User | None:  # noqa: A002
        """Get a single user by id."""
        # print("---------get")
        lb = LUser.nodes.get_or_none(uid=id.hex)
        return None if lb is None else User.from_lb(lb)

    async def get_by_email(self, email: str) -> User | None:
        """Get a single user by email."""
        # print("---------get by email")
        lb = LUser.nodes.get_or_none(email=email)
        return None if lb is None else User.from_lb(lb)

    async def get_by_oauth_account(
        self,
        oauth: str,  # noqa:ARG002
        account_id: str,
    ) -> User | None:
        """Get a single user by OAuth account id."""
        # print("---------get by oauth")
        la = LAccount.nodes.get_or_none(account_id=account_id)
        if la is None:
            return None
        lu = la.user.single()
        return User.from_lb(lu)

    async def create(self, create_dict: dict[str, Any]) -> User:
        """Create a user."""
        # print("------------ create")
        lb = LUser(**create_dict).save()
        return User.from_lb(lb)

    async def update(self, user: User, update_dict: dict) -> User:
        """Update a user."""
        # print("------------ update")
        lb = LUser.nodes.get(uid=user.id.hex)
        for key, value in update_dict.items():
            if value is None:
                continue
            setattr(lb, key, value)
        lb = lb.save()
        return User.from_lb(lb)

    async def delete(self, user: User) -> None:
        """Delete a user."""
        # print("------------ delete")
        lb = LUser.nodes.get(uid=user.id.hex)
        lb.delete()

    ########################################################### OAUTH
    async def add_oauth_account(
        self: BaseUserDatabase,
        user: User,
        create_dict: dict[str, Any],
    ) -> User:
        """Create an OAuth account and add it to the user."""
        # print("------------ add oauth account")
        account = Account.model_validate(create_dict)
        la = account.tolabel().save()
        lu = LUser.nodes.get(uid=user.id.hex)
        lu.refresh()
        lu.accounts.connect(la)
        return user

    async def update_oauth_account(
        self: BaseUserDatabase,
        user: User,
        oauth_account: Account,  # noqa: ARG002
        update_dict: dict[str, Any],
    ) -> User:
        """Update an OAuth account on a user."""
        print("------------ update oauth account", user, update_dict)  # noqa: T201

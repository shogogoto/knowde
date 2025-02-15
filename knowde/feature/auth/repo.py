"""DB."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from fastapi_users.db import BaseUserDatabase

from knowde.primitive.account import Account
from knowde.primitive.account.repo import LAccount

if TYPE_CHECKING:
    from fastapi_users.models import OAP, UOAP


class AccountDB(BaseUserDatabase[Account, UUID]):
    """DB adapter for fastapi-users."""

    async def get(self, id: UUID) -> Account | None:  # noqa: A002
        """Get a single user by id."""
        # print("---------get")
        lb = await LAccount.nodes.get_or_none(uid=id.hex)
        return None if lb is None else Account.from_lb(lb)

    async def get_by_email(self, email: str) -> Account | None:
        """Get a single user by email."""
        # print("---------get by email")
        lb = await LAccount.nodes.get_or_none(email=email)
        return None if lb is None else Account.from_lb(lb)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Account | None:
        """Get a single user by OAuth account id."""
        # print("---------get by oauth")
        lb = await LAccount.nodes.get_or_none(oauth_name=oauth, account_id=account_id)
        return Account.from_lb(lb)

    async def create(self, create_dict: dict[str, Any]) -> Account:
        """Create a user."""
        # print("------------ create")
        lb = await LAccount(**create_dict).save()
        return Account.from_lb(lb)

    async def update(self, user: Account, update_dict: dict) -> Account:
        """Update a user."""
        # print("------------ update")
        lb = await LAccount.nodes.get(uid=user.id.hex)
        for key, value in update_dict.items():
            if value is None:
                continue
            setattr(lb, key, value)
        lb = await lb.save()
        return Account.from_lb(lb)

    async def delete(self, user: Account) -> None:
        """Delete a user."""
        # print("------------ delete")
        lb = await LAccount.nodes.get(uid=user.id.hex)
        await lb.delete()

    async def add_oauth_account(
        self: BaseUserDatabase,
        user: UOAP,
        create_dict: dict[str, Any],
    ) -> UOAP:
        """Create an OAuth account and add it to the user."""
        # print("------------ add oauth account")

    async def update_oauth_account(
        self: BaseUserDatabase,
        user: UOAP,
        oauth_account: OAP,
        update_dict: dict[str, Any],
    ) -> UOAP:
        """Update an OAuth account on a user."""
        # print("------------ update oauth account")

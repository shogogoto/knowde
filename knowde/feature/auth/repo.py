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
        lb = LAccount.nodes.get_or_none(uid=id)
        return None if lb is None else Account.from_lb(lb)

    async def get_by_email(self, email: str) -> Account | None:
        """Get a single user by email."""
        lb = LAccount.nodes.get_or_none(email=email)
        if lb is None:
            return None
        return Account.from_lb(lb)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Account | None:
        """Get a single user by OAuth account id."""
        lb = LAccount.nodes.get_or_none(oauth_name=oauth, account_id=account_id)
        return Account.from_lb(lb)

    async def create(self, create_dict: dict[str, Any]) -> Account:
        """Create a user."""
        lb = LAccount(**create_dict).save()
        return Account.from_lb(lb)

    async def update(self, user: Account, update_dict: dict) -> Account:
        """Update a user."""
        lb = user.tolabel()
        for key, value in update_dict.items():
            setattr(lb, key, value)
        return Account.from_lb(lb.save())

    async def delete(self, user: Account) -> None:
        """Delete a user."""
        LAccount.delete(uid=user.id)

    async def add_oauth_account(
        self: BaseUserDatabase,
        user: UOAP,
        create_dict: dict[str, Any],
    ) -> UOAP:
        """Create an OAuth account and add it to the user."""

    async def update_oauth_account(
        self: BaseUserDatabase,
        user: UOAP,
        oauth_account: OAP,
        update_dict: dict[str, Any],
    ) -> UOAP:
        """Update an OAuth account on a user."""

"""user manager."""
from __future__ import annotations

import uuid
from functools import cache
from queue import Queue
from typing import Any, AsyncGenerator
from uuid import UUID

from fastapi import Request  # noqa: TCH002
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import (
    BaseUserDatabase,
)
from typing_extensions import override

from knowde.primitive.config.env import Settings
from knowde.primitive.user import Account, User
from knowde.primitive.user.repo import LAccount, LUser

s = Settings()


@cache
def response_queue() -> Queue:
    """レスポンスを保存するためのグローバルキュー."""
    return Queue()


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """from fastapi-users."""

    reset_password_token_secret = s.KN_AUTH_SECRET
    verification_token_secret = s.KN_AUTH_SECRET

    # @override
    # async def on_after_login(
    #     self,
    #     user: User,
    #     request: Request | None = None,
    #     response: Response | None = None,
    # ) -> None:
    #     """SSOのブラウザからのレスポンスを取得."""
    #     print("A" * 100)
    #     if response is not None:
    #         response_queue().put(response.body)

    @override
    async def on_after_register(
        self,
        user: User,
        request: Request | None = None,
    ) -> None:
        print(f"User {user.id}[{user.email}] has registered.")  # noqa: T201

    @override
    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ) -> None:
        print(  # noqa: T201
            f"User {user.id}[{self.email}] has forgot their password. "
            f"Reset token: {token}",
        )

    @override
    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ) -> None:
        print(  # noqa: T201
            f"Verification requested for user {user.id}[{self.email}]."
            f"Verification token: {token}",
        )


class AccountDB(BaseUserDatabase[User, UUID]):
    """DB adapter for fastapi-users."""

    async def get(self, id: UUID) -> User | None:  # noqa: A002
        """Get a single user by id."""
        # print("---------get")
        return User.get_or_none(uid=id.hex)

    async def get_by_email(self, email: str) -> User | None:
        """Get a single user by email."""
        # print("---------get by email")
        return User.get_or_none(email=email)

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


async def get_user_manager() -> AsyncGenerator:
    """For fastapi-users."""
    yield UserManager(AccountDB())


def auth_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    return AuthenticationBackend(
        name="jwt",
        transport=BearerTransport(tokenUrl="auth/jwt/login"),
        get_strategy=lambda: JWTStrategy(
            secret=s.KN_AUTH_SECRET,
            lifetime_seconds=s.KN_TOKEN_LIFETIME_SEC,
        ),
    )

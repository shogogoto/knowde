"""user manager."""

from __future__ import annotations

import uuid
from functools import cache
from queue import Queue
from typing import Any, override
from uuid import UUID

from fastapi import Request, Response
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import (
    BaseUserDatabase,
)

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

    @override
    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        """SSOのブラウザからのレスポンスを取得."""
        if response is not None and s.FRONTEND_URL is not None:
            response.status_code = 303
            response.headers["Location"] = s.FRONTEND_URL

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
            f"User {user.id}[{user.email}] has forgot their password. "
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
            f"Verification requested for user {user.id}[{user.email}]."
            f"Verification token: {token}",
        )


class AccountDB(BaseUserDatabase[User, UUID]):
    """DB adapter for fastapi-users."""

    @staticmethod
    async def get(id: UUID) -> User | None:  # noqa: A002
        """Get a single user by id."""
        # print("---------get")
        return User.get_or_none(uid=id.hex)

    @staticmethod
    async def get_by_email(email: str) -> User | None:
        """Get a single user by email."""
        # print("---------get by email")
        return User.get_or_none(email=email)

    @staticmethod
    async def get_by_oauth_account(
        oauth: str,  # noqa: ARG004
        account_id: str,
    ) -> User | None:
        """Get a single user by OAuth account id."""
        # print("---------get by oauth")
        la = LAccount.nodes.get_or_none(account_id=account_id)
        if la is None:
            return None
        lu = la.user.single()
        return User.from_lb(lu)

    @classmethod
    async def create(cls, create_dict: dict[str, Any]) -> User:
        """Create a user."""
        if await cls.get_by_email(create_dict["email"]):
            raise  # noqa: PLE0704

        lb = LUser(**create_dict).save()
        return User.from_lb(lb)

    @staticmethod
    async def update(user: User, update_dict: dict) -> User:
        """Update a user."""
        # print("------------ update")
        lb = LUser.nodes.get(uid=user.id.hex)
        for key, value in update_dict.items():
            if value is None:
                continue
            setattr(lb, key, value)
        lb = lb.save()
        return User.from_lb(lb)

    @staticmethod
    async def delete(user: User) -> None:
        """Delete a user."""
        # print("------------ delete")
        lb = LUser.nodes.get(uid=user.id.hex)
        lb.delete()

    # OAUTH
    @staticmethod
    async def add_oauth_account(
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

    @staticmethod
    async def update_oauth_account(
        user: User,
        oauth_account: Account,  # noqa: ARG004
        update_dict: dict[str, Any],
    ) -> User:
        """Update an OAuth account on a user."""
        print("------------ update oauth account", user, update_dict)  # noqa: T201


def get_user_manager() -> UserManager:
    """For fastapi-users."""
    return UserManager(AccountDB())


def bearer_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    return AuthenticationBackend(
        name="jwt",
        transport=BearerTransport(tokenUrl="auth/jwt/login"),
        get_strategy=lambda: JWTStrategy(
            secret=s.KN_AUTH_SECRET,
            lifetime_seconds=s.KN_TOKEN_LIFETIME_SEC,
        ),
    )


def cookie_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    return AuthenticationBackend(
        name="cookie",
        transport=CookieTransport(
            cookie_max_age=s.KN_TOKEN_LIFETIME_SEC,
            cookie_secure=s.COOKIE_SECURE,
            cookie_samesite=s.COOKIE_SAMESITE,
        ),
        get_strategy=lambda: JWTStrategy(
            secret=s.KN_AUTH_SECRET,
            lifetime_seconds=s.KN_TOKEN_LIFETIME_SEC,
        ),
    )

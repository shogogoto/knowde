"""user manager."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, AsyncGenerator

from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from typing_extensions import override

from knowde.feature.__core__.config import Settings
from knowde.feature.auth.repo import AccountDB
from knowde.primitive.account import Account

if TYPE_CHECKING:
    from fastapi import Request


s = Settings()


class UserManager(UUIDIDMixin, BaseUserManager[Account, uuid.UUID]):
    """from fastapi-users."""

    reset_password_token_secret = s.AUTH_SECRET
    verification_token_secret = s.AUTH_SECRET

    @override
    async def on_after_register(
        self,
        user: Account,
        request: Request | None = None,
    ) -> None:
        print(f"User {user.id} has registered.")  # noqa: T201

    @override
    async def on_after_forgot_password(
        self,
        user: Account,
        token: str,
        request: Request | None = None,
    ) -> None:
        print(f"User {user.id} has forgot their password. Reset token: {token}")  # noqa: T201

    @override
    async def on_after_request_verify(
        self,
        user: Account,
        token: str,
        request: Request | None = None,
    ) -> None:
        print(f"Verification requested for user {user.id}. Verification token: {token}")  # noqa: T201


async def get_user_manager() -> AsyncGenerator:
    """For fastapi-users."""
    yield UserManager(AccountDB())


def auth_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    return AuthenticationBackend(
        name="jwt",
        transport=BearerTransport(tokenUrl="auth/jwt/login"),
        get_strategy=lambda: JWTStrategy(secret=s.AUTH_SECRET, lifetime_seconds=3600),
    )


def router_creator() -> FastAPIUsers:
    """Crreate users router creator."""
    return FastAPIUsers[Account, uuid.UUID](get_user_manager, [auth_backend()])

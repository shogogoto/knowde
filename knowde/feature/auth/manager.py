"""user manager."""
from __future__ import annotations

import uuid
from typing import AsyncGenerator

from fastapi import Request  # noqa: TCH002
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from typing_extensions import override

from knowde.feature.__core__.config import Settings
from knowde.feature.auth.repo import AccountDB
from knowde.primitive.account import User

s = Settings()


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """from fastapi-users."""

    reset_password_token_secret = s.KN_AUTH_SECRET
    verification_token_secret = s.KN_AUTH_SECRET

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


async def get_user_manager() -> AsyncGenerator:
    """For fastapi-users."""
    yield UserManager(AccountDB())


def auth_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    s = Settings()
    return AuthenticationBackend(
        name="jwt",
        transport=BearerTransport(tokenUrl="auth/jwt/login"),
        get_strategy=lambda: JWTStrategy(
            secret=s.KN_AUTH_SECRET,
            lifetime_seconds=s.JWT_LIFETIME_SEC,
        ),
    )


def router_creator() -> FastAPIUsers:
    """Crreate users router creator."""
    return FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend()])

"""managerはevent trigger, observer."""

from __future__ import annotations

import uuid
from typing import override

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from knowde.config.env import Settings
from knowde.feature.auth.db import AccountDB
from knowde.feature.auth.repo import User

s = Settings()


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
    #     if response is not None and s.FRONTEND_URL is not None:
    #         await super().get_login_response(user, response, self)
    #         response.status_code = 303
    #         response.headers["Location"] = s.FRONTEND_URL

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


def get_user_manager() -> UserManager:
    """For fastapi-users."""
    return UserManager(AccountDB())

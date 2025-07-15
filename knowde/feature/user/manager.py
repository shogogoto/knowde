"""managerはevent trigger, observer."""

from __future__ import annotations

import logging
import uuid
from typing import override

from fastapi_users import BaseUserManager, UUIDIDMixin

from knowde.config.env import Settings
from knowde.feature.user.domain import User

from .repo.db import AccountDB

s = Settings()


logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """from fastapi-users."""

    reset_password_token_secret = s.KN_AUTH_SECRET
    verification_token_secret = s.KN_AUTH_SECRET

    @override
    async def on_after_login(self, user, request=None, response=None):
        logger.info("User has logged in. %s", user.id)

    @override
    async def on_after_register(self, user: User, request=None) -> None:
        logger.info("User has registered. %s", user.id)

    @override
    async def on_after_forgot_password(self, user, token, request=None):
        logger.info("User has forgot password. %s", user.id)

    @override
    async def on_after_request_verify(self, user, token, request=None):
        logger.info("User has requested email verification. %s", user.id)


def get_user_manager() -> UserManager:
    """For fastapi-users."""
    return UserManager(AccountDB())

"""認証."""

from __future__ import annotations

from functools import cache
from typing import Final
from uuid import UUID

from fastapi_users import FastAPIUsers

from knowde.feature.user.backend import bearer_backend, cookie_backend
from knowde.feature.user.domain import User
from knowde.feature.user.manager import get_user_manager

PREFIX_USER: Final = "/user"


@cache
def auth_component() -> FastAPIUsers:
    """fastapi-usersの設定."""
    return FastAPIUsers[User, UUID](
        get_user_manager,
        [bearer_backend(), cookie_backend()],
    )

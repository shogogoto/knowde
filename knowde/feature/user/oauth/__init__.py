"""oauth."""

from typing import override

from fastapi import Response
from fastapi_users import models
from fastapi_users.authentication import (
    AuthenticationBackend,
    Strategy,
)

from knowde.config.env import Settings
from knowde.feature.user.backend import get_cookie_transport, get_strategy

s = Settings()


class RedirectCookieAuthentication(AuthenticationBackend):
    """cookie認証後のリダイレクト先を設定する."""

    @override
    async def login(
        self,
        strategy: Strategy[models.UP, models.ID],
        user: models.UP,
    ) -> Response:
        res = await super().login(strategy, user)
        if s.FRONTEND_URL is not None:
            res.status_code = 303
            res.headers["Location"] = s.FRONTEND_URL
        return res


def google_cookie_backend() -> AuthenticationBackend:
    """For fastapi-users."""
    return RedirectCookieAuthentication(
        name="cookie",
        transport=get_cookie_transport(),
        get_strategy=get_strategy,
    )

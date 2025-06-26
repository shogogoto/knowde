"""oauth router."""

from __future__ import annotations

from fastapi import APIRouter
from httpx_oauth.clients.google import GoogleOAuth2

from knowde.config.env import Settings
from knowde.feature.user import auth_component
from knowde.feature.user.backend import bearer_backend

from . import google_cookie_backend

ac = auth_component()

s = Settings()
_r = APIRouter(prefix="/google", tags=["google"])
google = GoogleOAuth2(s.GOOGLE_CLIENT_ID, s.GOOGLE_CLIENT_SECRET)

_r.include_router(
    ac.get_oauth_router(
        google,
        bearer_backend(),
        s.KN_AUTH_SECRET,
    ),
)
_r.include_router(
    ac.get_oauth_router(
        google,
        google_cookie_backend(),
        s.KN_AUTH_SECRET,
        redirect_url=s.KN_REDIRECT_URL,
        associate_by_email=True,
        # is_verified_by_default=True,
    ),
    prefix="/cookie",
)


def google_router() -> APIRouter:
    """Google SSO用."""
    return _r

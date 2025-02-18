"""googl sso router."""
from enum import Enum
from typing import Final, TypedDict
from uuid import UUID

from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from httpx_oauth.clients.google import GoogleOAuth2
from pydantic_core import Url

from knowde.feature.__core__.config import Settings
from knowde.feature.auth.manager import auth_backend, get_user_manager
from knowde.primitive.account import User


class Provider(Enum):
    """Single Sign on provider."""

    GOOGLE = "google"


class GoogleSSOResponse(TypedDict):
    """SSOレスポンス."""

    id: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    picture: Url
    provider: Provider


GOOGLE_URL: Final = "/google"


def router_google_oauth() -> APIRouter:
    """For fastapi-users."""
    s = Settings()
    rc = FastAPIUsers[User, UUID](get_user_manager, [auth_backend()])
    return rc.get_oauth_router(
        GoogleOAuth2(s.GOOGLE_CLIENT_ID, s.GOOGLE_CLIENT_SECRET),
        auth_backend(),
        s.KN_AUTH_SECRET,
        # redirect_url="/google/callback",
        # associate_by_email=True,
        # is_verified_by_default=True,
    )

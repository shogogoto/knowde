"""認証."""

from __future__ import annotations

from functools import cache
from uuid import UUID

from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from httpx_oauth.clients.google import GoogleOAuth2

from knowde.complex.auth import PREFIX_USER
from knowde.primitive.config.env import Settings
from knowde.primitive.user import User

from .manager import auth_backend, get_user_manager
from .schema import UserCreate, UserRead, UserUpdate


@cache
def auth_component() -> FastAPIUsers:
    """fastapi-usersの設定."""
    return FastAPIUsers[User, UUID](get_user_manager, [auth_backend()])


ac = auth_component()
user_router = APIRouter(prefix=PREFIX_USER, tags=["user"])
user_router.include_router(ac.get_users_router(UserRead, UserUpdate))

auth_router = APIRouter(tags=["auth"])
pref_auth = APIRouter(prefix="/auth")
pref_auth.include_router(ac.get_auth_router(auth_backend()), prefix="/jwt")
pref_auth.include_router(ac.get_register_router(UserRead, UserCreate))
pref_auth.include_router(ac.get_reset_password_router())
pref_auth.include_router(ac.get_verify_router(UserRead))
auth_router.include_router(pref_auth)


s = Settings()
auth_router.include_router(
    ac.get_oauth_router(
        GoogleOAuth2(s.GOOGLE_CLIENT_ID, s.GOOGLE_CLIENT_SECRET),
        auth_backend(),
        s.KN_AUTH_SECRET,
        # redirect_url="/google/callback",
        # associate_by_email=True,
        # is_verified_by_default=True,
    ),
    prefix="/google",
    tags=["auth"],
)

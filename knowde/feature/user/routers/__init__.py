"""認証."""

from __future__ import annotations

from fastapi import APIRouter

from knowde.feature.user import PREFIX_USER
from knowde.feature.user.backend import bearer_backend, cookie_backend
from knowde.feature.user.oauth.router import google_router
from knowde.feature.user.routers.public import public_user_router
from knowde.feature.user.schema import UserCreate, UserRead, UserUpdate
from knowde.shared.user.router_util import auth_component

ac = auth_component()

_auth_router = APIRouter()
pref_auth = APIRouter(prefix="/auth", tags=["auth"])
pref_auth.include_router(ac.get_auth_router(bearer_backend()), prefix="/jwt")
pref_auth.include_router(ac.get_auth_router(cookie_backend()), prefix="/cookie")
pref_auth.include_router(ac.get_register_router(UserRead, UserCreate))
pref_auth.include_router(ac.get_reset_password_router())
pref_auth.include_router(ac.get_verify_router(UserRead))
_auth_router.include_router(pref_auth)

_auth_router.include_router(google_router())

_user_router = APIRouter(prefix=PREFIX_USER)
# こちらを先に定義しないと/user/searchの代わりに/user/{id}が呼ばれてしまう
_user_router.include_router(public_user_router())
_user_router.include_router(ac.get_users_router(UserRead, UserUpdate), tags=["user"])


def auth_router() -> APIRouter:
    """Auth router."""
    return _auth_router


def user_router() -> APIRouter:
    """User router."""
    return _user_router

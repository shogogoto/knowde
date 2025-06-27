"""認証."""

from __future__ import annotations

from fastapi import APIRouter

from knowde.feature.user import PREFIX_USER
from knowde.feature.user.backend import bearer_backend, cookie_backend
from knowde.feature.user.oauth.router import google_router
from knowde.feature.user.schema import UserCreate, UserRead, UserUpdate
from knowde.shared.user import auth_component

ac = auth_component()

auth_router = APIRouter()
pref_auth = APIRouter(prefix="/auth", tags=["auth"])
pref_auth.include_router(ac.get_auth_router(bearer_backend()), prefix="/jwt")
pref_auth.include_router(ac.get_auth_router(cookie_backend()), prefix="/cookie")
pref_auth.include_router(ac.get_register_router(UserRead, UserCreate))
pref_auth.include_router(ac.get_reset_password_router())
pref_auth.include_router(ac.get_verify_router(UserRead))
auth_router.include_router(pref_auth)

auth_router.include_router(google_router())

user_router = APIRouter(prefix=PREFIX_USER, tags=["user"])
user_router.include_router(ac.get_users_router(UserRead, UserUpdate))


# @user_router.get("/me")
# async def read_users_me(
#     user: UserRead = Depends(ac.get_current_active_user),
# ) -> UserRead:
#     return user

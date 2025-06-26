"""認証."""

from __future__ import annotations

from fastapi import APIRouter

from knowde.feature.auth.backend import bearer_backend, cookie_backend
from knowde.feature.auth.oauth.router import google_router

from . import PREFIX_USER, auth_component
from .schema import UserCreate, UserRead, UserUpdate

ac = auth_component()
user_router = APIRouter(prefix=PREFIX_USER, tags=["user"])
user_router.include_router(ac.get_users_router(UserRead, UserUpdate))

auth_router = APIRouter()
pref_auth = APIRouter(prefix="/auth", tags=["auth"])
pref_auth.include_router(ac.get_auth_router(bearer_backend()), prefix="/jwt")
pref_auth.include_router(ac.get_auth_router(cookie_backend()), prefix="/cookie")
pref_auth.include_router(ac.get_register_router(UserRead, UserCreate))
pref_auth.include_router(ac.get_reset_password_router())
pref_auth.include_router(ac.get_verify_router(UserRead))
auth_router.include_router(pref_auth)
auth_router.include_router(google_router())

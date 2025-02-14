"""認証."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers

from knowde.feature.auth.schema import UserCreate, UserRead, UserUpdate
from knowde.feature.auth.users import auth_backend, get_user_manager
from knowde.primitive.account import Account

from .sso.route import router_google_sso

if TYPE_CHECKING:
    from .domain import (
        User,
    )

auth_router = APIRouter()
auth_router.include_router(router_google_sso())

rc = FastAPIUsers[Account, UUID](get_user_manager, [auth_backend()])

auth_router.include_router(
    rc.get_auth_router(auth_backend()),
    prefix="/auth/jwt",
    tags=["auth"],
)
auth_router.include_router(
    rc.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
auth_router.include_router(
    rc.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
auth_router.include_router(
    rc.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
auth_router.include_router(
    rc.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@auth_router.get("/authenticated-route")
async def authenticated_route(
    user: User = Depends(rc.current_user(active=True)),
) -> dict:
    """ナンジャコリャ."""
    return {"message": f"Hello {user.email}!"}

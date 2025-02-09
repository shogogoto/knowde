"""認証."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from knowde.feature.auth.domain import User, fake_hash_password
from knowde.feature.auth.repo import UserInDB, fake_decode_token, fake_users_db

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.get("/items/")
async def read_items(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    """Tutorial."""
    return {"token": token}


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Tutorial."""
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Tutorial."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """Tutorial."""
    user_dict = fake_users_db().get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@auth_router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """tutorial."""
    return current_user

"""認証."""
from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JOSEError, jwt

from knowde.feature.auth.domain import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    Token,
    TokenData,
    User,
    create_access_token,
)
from knowde.feature.auth.repo import (
    authenticate_user,
    fake_users_db,
    get_user,
)

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.get("/items/")
async def read_items(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    """Tutorial."""
    return {"token": token}


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Tutorial."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JOSEError as e:
        raise credentials_exception from e
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    token_data = TokenData(username=username)
    user = get_user(fake_users_db(), username=token_data.username)
    # user = fake_decode_token(token)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Tutorial."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@auth_router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Tutorial."""
    user = authenticate_user(fake_users_db(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},  # userの識別情報 リソースの識別子 権限の種類など
        # userが存在しなくても、JWTトークンがあれば操作可能
        # idが被らないようにprefixつけがち
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")  # noqa: S106


@auth_router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """tutorial."""
    return current_user


@auth_router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list:
    """tutorial."""
    return [{"item_id": "Foo", "owner": current_user.username}]

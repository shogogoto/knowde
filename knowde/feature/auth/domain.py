"""domain model."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # noqa: S105
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """tutorial."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """tutorial."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """tutorial."""
    return pwd_context.hash(password)


class User(BaseModel):
    """tutorial."""

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def fake_hash_password(password: str) -> str:
    """Tutorial."""
    return "fakehashed" + password


class Token(BaseModel):
    """Tutorial."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Tutorial."""

    username: str | None = None

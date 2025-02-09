"""DB."""
from __future__ import annotations

from typing import Literal

from knowde.feature.auth.domain import User, verify_password


def fake_users_db() -> dict:
    """Db."""
    return {
        "johndoe": {
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # noqa: E501
            "disabled": False,
        },
    }


class UserInDB(User):
    """tutorial."""

    hashed_password: str


def get_user(db: dict, username: str | None) -> UserInDB | None:
    """tutorial."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def fake_decode_token(token: str) -> User | None:
    """tutorial."""
    return get_user(fake_users_db(), token)


def authenticate_user(
    db: dict,
    username: str,
    password: str,
) -> Literal[False] | UserInDB:
    """tutorial."""
    user = get_user(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        return False
    return user

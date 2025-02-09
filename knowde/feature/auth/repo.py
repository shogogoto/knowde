"""DB."""
from __future__ import annotations

from knowde.feature.auth.domain import User


def fake_users_db() -> dict:
    """Db."""
    return {
        "johndoe": {
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "hashed_password": "fakehashedsecret",
            "disabled": False,
        },
        "alice": {
            "username": "alice",
            "full_name": "Alice Wonderson",
            "email": "alice@example.com",
            "hashed_password": "fakehashedsecret2",
            "disabled": True,
        },
    }


class UserInDB(User):
    """tutorial."""

    hashed_password: str


def get_user(db: dict, username: str) -> User | None:
    """tutorial."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def fake_decode_token(token: str) -> User | None:
    """Check the next version."""
    return get_user(fake_users_db, token)

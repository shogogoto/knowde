"""domain model."""
from __future__ import annotations

from pydantic import BaseModel


class User(BaseModel):
    """tutorial."""

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def fake_hash_password(password: str) -> str:
    """Tutorial."""
    return "fakehashed" + password

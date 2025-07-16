"""認証."""

from __future__ import annotations

from typing import Final

from pydantic import BaseModel, Field

PREFIX_USER: Final = "/user"
LEN_DISPLAY_NAME: Final = 32
MAX_LEN_USERNAME: Final = 16
LEN_PROFILE: Final = 160  # twitterと同じらしい


class CommonSchema(BaseModel):  # noqa: D101
    display_name: str | None = Field(default=None, max_length=LEN_DISPLAY_NAME)
    profile: str | None = Field(default=None, max_length=LEN_PROFILE)
    avatar_url: str | None = None
    username: str | None = Field(
        default=None,
        pattern=r"^[^-]*$",
        max_length=MAX_LEN_USERNAME,
    )

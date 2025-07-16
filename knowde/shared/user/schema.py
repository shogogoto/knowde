"""shared user schema."""

from datetime import datetime

from pydantic import BaseModel, Field

from . import LEN_DISPLAY_NAME, LEN_PROFILE, MAX_LEN_USERNAME


class CommonSchema(BaseModel):  # noqa: D101
    display_name: str | None = Field(default=None, max_length=LEN_DISPLAY_NAME)
    profile: str | None = Field(default=None, max_length=LEN_PROFILE)
    avatar_url: str | None = None
    username: str | None = Field(
        default=None,
        pattern=r"^[^-]*$",
        max_length=MAX_LEN_USERNAME,
    )


class UserReadPublic(CommonSchema):
    """公開ユーザー情報."""

    created: datetime

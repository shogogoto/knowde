"""shared user schema."""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field

from knowde.shared.types import to_uuid
from knowde.shared.util import Neo4jDateTime

from . import LEN_DISPLAY_NAME, LEN_PROFILE, MAX_LEN_USERNAME


class CommonSchema(BaseModel):  # noqa: D101
    display_name: str | None = Field(default=None, max_length=LEN_DISPLAY_NAME)
    profile: str | None = Field(default=None, max_length=LEN_PROFILE)
    avatar_url: str | None = None
    username: str | None = Field(
        default=None,
        pattern=r"^[a-zA-Z0-9_-]+$",
        max_length=MAX_LEN_USERNAME,
        title="ユーザー名",
        description="半角英数字とハイフン、アンダースコアのみが使用できます。",
    )


class UserReadPublic(CommonSchema):
    """公開ユーザー情報."""

    id: Annotated[UUID, BeforeValidator(to_uuid)] = Field(alias="uid")
    created: Neo4jDateTime

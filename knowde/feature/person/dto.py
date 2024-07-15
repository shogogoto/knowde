"""Data Transfer Object."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PersonAddParam(BaseModel, frozen=True):
    """Person DTO."""

    name: str = Field(description="人物名")
    birth: Optional[str] = Field(default=None, description="誕生日")
    death: Optional[str] = Field(default=None, description="命日")


class PersonRenameParam(BaseModel, frozen=True):
    """Person DTO."""

    name: str = Field(description="人物名")


# class AuthorParam(BaseModel, frozen=True):
#     name: str
#     # 別フィーチャーに分離するかも
#     birth: LifeDate | None = Field(default=None, title="誕生日")
#     death: LifeDate | None = Field(default=None, title="命日")


# OptionalAuthorParam = create_partial_model(AuthorParam)

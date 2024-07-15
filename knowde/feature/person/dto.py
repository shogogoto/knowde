"""Data Transfer Object."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PersonAddParam(BaseModel, frozen=True):
    """Person DTO."""

    name: str
    birth: Optional[str] = None
    death: Optional[str] = None


# class AuthorParam(BaseModel, frozen=True):
#     name: str
#     # 別フィーチャーに分離するかも
#     birth: LifeDate | None = Field(default=None, title="誕生日")
#     death: LifeDate | None = Field(default=None, title="命日")


# OptionalAuthorParam = create_partial_model(AuthorParam)

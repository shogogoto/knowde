from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_partial.partial import create_partial_model

if TYPE_CHECKING:
    from knowde._feature.person.domain import LifeDate


class AuthorParam(BaseModel, frozen=True):
    name: str
    # 別フィーチャーに分離するかも
    birth: LifeDate | None = Field(default=None, title="誕生日")
    death: LifeDate | None = Field(default=None, title="命日")


OptionalAuthorParam = create_partial_model(AuthorParam)

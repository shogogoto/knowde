"""パースで得られるデータ."""
from __future__ import annotations

from datetime import date  # noqa: TCH003

from pydantic import BaseModel, Field


class SourceAbout(BaseModel, frozen=True):
    """情報源について."""

    title: str = Field(title="情報源のタイトル")
    author: str | None = Field(default=None, title="著者")
    published: date | None = Field(default=None, title="第一出版日")

    @property
    def tuple(self) -> tuple[str, str | None, date | None]:  # noqa: D102
        return (self.title, self.author, self.published)

    def contains(self, title: str) -> bool:
        """タイトルに含まれた文字列か."""
        return title in self.title

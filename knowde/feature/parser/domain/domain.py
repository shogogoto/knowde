"""パースで得られるデータ."""
from __future__ import annotations

from datetime import date  # noqa: TCH003

from lark import Token, Tree
from pydantic import BaseModel, Field

from knowde.feature.parser.domain.errors import LineMismatchError


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


line_types = ["ONELINE", "MULTILINE"]


def get_line(t: Tree) -> str:
    """Line treeから値を1つ返す."""
    # 直下がlineだった場合
    cl = t.children
    first = cl[0]
    if isinstance(first, Token) and first.type in line_types:
        return str(first)
    if isinstance(first, Tree):
        if first.data == "ctx":
            return get_line(first.children[1])
        return get_line(first)
    raise LineMismatchError

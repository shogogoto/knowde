"""パースで得られるデータ."""
from __future__ import annotations

from datetime import date  # noqa: TCH003

from lark import Token, Tree
from pydantic import BaseModel, Field

from knowde.feature.parser.domain.errors import LineMismatchError


class StatementSpace(BaseModel):
    """言明スコープ."""


class Heading(BaseModel, frozen=True):
    """見出しまたは章節."""

    title: str
    level: int = Field(ge=1, le=6)

    def __str__(self) -> str:
        """For user string."""
        return f"h{self.level}={self.title}"

    def contains(self, title: str) -> bool:
        """タイトルを含んでいるか."""
        return title in self.title


class SourceInfo(BaseModel, frozen=True):
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


class Namespace(BaseModel):
    """知識の有効範囲."""

    parent: Heading
    children: list[Heading] = Field(default_factory=list)
    names: dict = Field(default_factory=dict)
    statements: list[str] = Field(default_factory=list)


class Comment(BaseModel, frozen=True):
    """コメント."""

    value: str

    def __str__(self) -> str:
        """For user string."""
        return f"!{self.value}"


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

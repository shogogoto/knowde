"""情報源ツリー."""
from __future__ import annotations

from datetime import date  # noqa: TCH003
from typing import Self

from lark import Tree  # noqa: TCH002
from pydantic import BaseModel, Field, field_validator


class SourceAbout(BaseModel, frozen=True):
    """情報源について."""

    title: str = Field(title="情報源のタイトル")
    author: str | None = Field(default=None, title="著者")
    published: date | None = Field(default=None, title="第一出版日")

    @property
    def tuple(self) -> tuple[str, str | None, date | None]:  # noqa: D102
        return (self.title, self.author, self.published)


class SourceMismatchError(Exception):
    """ソースが特定できない."""


class SourceAboutMultiHitError(Exception):
    """情報源については１つだけ."""


class SourceTree(BaseModel, frozen=True, arbitrary_types_allowed=True):
    """１つの情報源."""

    tree: Tree = Field(description="h1をrootとする")

    @field_validator("tree")
    @classmethod
    def _validate(cls, t: Tree) -> Tree:
        if t.data != "h1":
            msg = f"must h1 Tree: {t.data}"
            raise ValueError(msg)
        return t

    @classmethod
    def create(cls, t: Tree, title: str) -> Self:  # noqa: D102
        hs = t.find_data("h1")
        ls = [h for h in hs if title in h.children[0].title]
        if len(ls) == 1:
            return cls(tree=ls[0])
        raise SourceMismatchError

    @property
    def about(self) -> SourceAbout:
        """情報源について."""
        abouts = list(self.tree.find_data("source_about"))
        if len(abouts) > 1:
            raise SourceAboutMultiHitError
        author, published = None, None
        if len(abouts) == 1:
            author, published = abouts[0].children
        return SourceAbout(title=self.title, author=author, published=published)

    @property
    def title(self) -> str:
        """ソースタイトル."""
        return self.tree.children[0].title

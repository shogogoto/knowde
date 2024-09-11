"""情報源ツリー."""
from __future__ import annotations

from datetime import date  # noqa: TCH003
from typing import Self

from lark import Tree, Visitor
from pydantic import BaseModel, Field

from knowde.feature.parser.domain.domain import SourceInfo


class SourceMatchError(Exception):
    """ソースが特定できない."""


class SourceVisitor(BaseModel, Visitor):
    """構文木から情報源の情報を取り出す.

    二回目の代入があったらエラー
    """

    title: str = ""
    author: str | None = None
    published: date | None = None

    def h1(self, t: Tree) -> None:  # noqa: D102
        if self.title != "":
            raise SourceMatchError
        self.title = t.children[0].title

    def source_info(self, t: Tree) -> None:  # noqa: D102
        if self.author is not None or self.published is not None:
            raise SourceMatchError
        self.author, self.published = t.children

    @property
    def info(self) -> SourceInfo:  # noqa: D102
        return SourceInfo(
            title=self.title,
            author=self.author,
            published=self.published,
        )


class NameConflictError(Exception):
    """名前衝突."""


class SourceTree(BaseModel, frozen=True, arbitrary_types_allowed=True):
    """１つの情報源."""

    info: SourceInfo
    tree: Tree = Field(description="h1をrootとする")

    @classmethod
    def create(cls, t: Tree) -> Self:  # noqa: D102
        v = SourceVisitor()
        v.visit(t)
        return cls(tree=t, info=v.info)

    # @property
    # def names(self) -> None:
    #     pass


class NameCollectionVisitor(BaseModel, Visitor):
    """名前を集める."""

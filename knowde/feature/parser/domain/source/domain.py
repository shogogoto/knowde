"""情報源ツリー."""
from __future__ import annotations

from collections import Counter
from datetime import date  # noqa: TCH003
from typing import Self

from lark import Token, Tree, Visitor
from pydantic import BaseModel, Field

from knowde.feature.parser.domain.errors import TermConflictError
from knowde.feature.parser.domain.statement import Statement, StatementVisitor


class SourceMatchError(Exception):
    """ソースが特定できない."""


def get_source(t: Tree, title: str) -> SourceTree:
    """情報源とその知識ツリー."""
    hs = t.find_data("h1")
    ls = [h for h in hs if title in h.children[0].title]
    if len(ls) == 1:
        return SourceTree.create(ls[0])
    raise SourceMatchError


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

    def source_about(self, t: Tree) -> None:  # noqa: D102
        if self.author is not None or self.published is not None:
            raise SourceMatchError
        self.author, self.published = t.children

    @property
    def about(self) -> SourceAbout:  # noqa: D102
        return SourceAbout(
            title=self.title,
            author=self.author,
            published=self.published,
        )


def check_name_conflict(names: list[str]) -> None:
    """名前の重複チェック."""
    dups = [(name, c) for name, c in Counter(names).items() if c > 1]
    if len(dups) > 0:
        msg = f"次の名前が重複しています:{dups}"
        raise TermConflictError(msg)


class SourceTree(BaseModel, frozen=True, arbitrary_types_allowed=True):
    """１つの情報源."""

    about: SourceAbout
    tree: Tree = Field(description="h1をrootとする")

    @classmethod
    def create(cls, t: Tree) -> Self:  # noqa: D102
        v = SourceVisitor()
        v.visit(t)
        self = cls(tree=t, about=v.about)
        check_name_conflict(self.names)
        return self

    @property
    def names(self) -> list[str]:
        """名前一覧."""
        ls = []
        for n in self.tree.find_data("name"):
            ls.extend(n.children)
        return [str(e) for e in ls]

    @property
    def rep_names(self) -> list[str]:
        """代表名一覧."""
        ls = [d.children[0] for d in self.tree.find_data("name")]
        return [str(e) for e in ls]

    @property
    def aliases(self) -> list[str]:
        """代表名一覧."""
        vs = self.tree.scan_values(lambda x: isinstance(x, Token) and x.type == "ALIAS")
        return [str(e) for e in vs]

    def statement(self, s: str) -> Statement:
        """context付きの言明を返す."""
        v = StatementVisitor()
        v.visit(self.tree)
        return Statement.create(s, v.g)

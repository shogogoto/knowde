"""情報源ツリー."""
from __future__ import annotations

from datetime import date  # noqa: TCH003
from functools import cached_property
from typing import Self

from lark import Tree  # noqa: TCH002
from pydantic import BaseModel, Field, field_validator

from knowde.feature.parser.domain.parser.transfomer.heading import Heading


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
        return SourceAbout(
            title=self.root.title,
            author=author,
            published=published,
        )

    @property
    def root(self) -> Heading:  # noqa: D102
        return self.tree.children[0]

    def children(self, h: Heading) -> list[Heading]:
        """最も近い階層の子見出しを取得."""
        self._check_contains(h)
        _children = [e for e in self.headings if e.level > h.level]
        lvs = [c.level for c in _children]
        lv = min(lvs) if len(lvs) != 0 else 999  # large enough dummy number
        return [e for e in self.headings if e.level == lv]

    def parent(self, h: Heading) -> Heading | None:
        """最も近い親見出し."""
        self._check_contains(h)
        # parents = [e for e in self.headings if e.level < h.level]
        # lv = min([c.level for c in parents])

    @cached_property
    def headings(self) -> list[Heading]:
        """全ての見出し."""
        types = [f"h{i}" for i in range(1, 7)]
        return [t.children[0] for t in self.tree.find_pred(lambda x: x.data in types)]

    def _check_contains(self, h: Heading) -> None:
        if h not in self.headings:
            msg = f"{h} is not contained"
            raise KeyError(msg)

    def _contains(self, h1: Heading, h2: Heading) -> None:
        pass

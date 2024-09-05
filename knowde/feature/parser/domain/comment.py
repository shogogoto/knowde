"""comment."""
from __future__ import annotations

from typing import override

from lark import Token, Transformer, Tree
from pydantic import BaseModel, Field, RootModel

from knowde.feature.parser.domain.heading import Heading, THeading
from knowde.feature.parser.domain.parser import CommonVisitor, transparse


class Comment(BaseModel, frozen=True):
    """コメント."""

    value: str

    def __str__(self) -> str:
        """For user string."""
        return f"!{self.value}"


class Comments(RootModel[list[Comment]]):
    """コメントリスト."""

    @property
    def strs(self) -> list[str]:
        """タイトルのリスト."""
        return [c.value for c in self.root]


class TComment(Transformer):
    """comment transformer."""

    def COMMENT(self, tok: Token) -> Comment:  # noqa: N802
        """! hogehoge."""
        return Comment(value=tok.replace("!", "").strip())


class CommentDict(dict[Heading, Comments]):
    """見出しに紐付いたコメントの辞書."""

    def strs(self, title: str) -> list[str]:
        """タイトルのリスト."""
        return self[self.heading(title)].strs

    def heading(self, title: str) -> Heading:
        """タイトルから見出しを取得."""
        return next(filter(lambda x: title in x.value, self.keys()))


class CommentVisitor(BaseModel, CommonVisitor, arbitrary_types_allowed=True):
    """見出しにコメントを属させる."""

    d: CommentDict = Field(default_factory=CommentDict)

    @override
    def do(self, tree: Tree) -> None:
        """For Rule."""
        c = tree.children
        heading: Heading = c[0]
        cmts = Comments(root=[v for v in c[1:] if isinstance(v, Comment)])
        self.d[heading] = cmts


def load_with_comment(text: str) -> CommentDict:
    """With comment."""
    _trans = TComment() * THeading()
    _tree = transparse(text, _trans)
    v = CommentVisitor()
    v.visit(_tree)
    return v.d

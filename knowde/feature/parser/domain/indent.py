"""インデントの処理."""
from __future__ import annotations

from typing import Any

from lark import Tree
from lark.visitors import Visitor_Recursive
from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.core.errors.errors import DomainError
from knowde.core.types import NXGraph  # noqa: TCH001


class IndentTreeNotFoundError(DomainError):
    """ツリーがないンゴ."""


def has_only_child(t: Tree) -> bool:
    """一人っ子."""
    return len(t.children) == 1


def has_subtree(t: Tree) -> bool:  # noqa: D103
    subs = [c for c in t.children if isinstance(c, Tree)]
    return len(subs) > 0


# def get_subchild(children: list[Token | Tree]) -> Tree:
#     for c in children:
#         if isinstance(c, Tree):
#             return c
#     raise IndentTreeNotFoundError


class IndentRule(BaseModel, Visitor_Recursive):
    """インデントツリー作成."""

    g: NXGraph = Field(default_factory=DiGraph)

    def tree(self, t: Tree) -> None:  # noqa: D102
        c = t.children
        if len(c) == 1:
            return


class IndentTree(BaseModel, frozen=True):
    """見出しの階層."""

    g: NXGraph

    @property
    def nodes(self) -> set:
        """Heading nodes."""
        return set(self.g.nodes)

    @property
    def count(self) -> int:
        """Total number of heading."""
        return len(self.nodes)

    def get(self, title: str) -> Any:  # noqa: ANN401
        """見出しを特定."""
        _f = list(filter(lambda x: title in x.value, self.nodes))
        if len(_f) == 0:
            msg = f"{title}を含む見出しはありません"
            raise KeyError(msg)
        if len(_f) > 1:
            msg = f"{title}を含む見出しが複数見つかりました"
            raise KeyError(msg)
        return _f[0]

    def info(self, title: str) -> tuple[int, int]:
        """Return level and Count children for test."""
        h = self.get(title)
        children = self.g[h]
        return (h.level, len(children))

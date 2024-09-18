"""knowde AST."""
from __future__ import annotations

from lark import Tree  # noqa: TCH002
from pydantic import BaseModel

from knowde.feature.parser.domain.source import SourceMatchError, SourceTree


class RootTree(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    """parseして得られたCSTを変換."""

    tree: Tree

    def get_source(self, title: str) -> SourceTree:
        """情報源とその知識ツリー."""
        hs = self.tree.find_data("h1")
        ls = [h for h in hs if title in h.children[0].title]
        if len(ls) == 1:
            return SourceTree.create(ls[0])
        raise SourceMatchError

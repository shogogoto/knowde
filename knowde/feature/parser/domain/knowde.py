"""knowde AST."""
from __future__ import annotations

from lark import Tree  # noqa: TCH002
from pydantic import BaseModel

from knowde.feature.parser.domain.domain import SourceInfo
from knowde.feature.parser.domain.source import SourceVisitor


class KnowdeTree(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    """parseして得られた情報."""

    tree: Tree

    def get_source(self, title: str) -> SourceInfo:
        """情報源とその知識ツリー."""
        v = SourceVisitor()
        v.visit(self.tree)
        return v.get(title)

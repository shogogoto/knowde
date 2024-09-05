"""parser."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from lark import Lark, Transformer, Tree
from lark.visitors import Visitor_Recursive

if TYPE_CHECKING:
    from lark.visitors import TransformerChain


@cache
def common_parser() -> Lark:
    """Lark Parser."""
    p = Path(__file__).parent / "input.lark"
    return Lark(
        p.read_text(),
        parser="lalr",
        # ambiguity="explicit",
        # debug=True,
    )


def transparse(text: str, t: Transformer | TransformerChain) -> Tree:
    """Parse and transform."""
    _tree = common_parser().parse(text)
    return t.transform(_tree)


class CommonVisitor(Visitor_Recursive, ABC):
    """共通ルール."""

    @abstractmethod
    def do(self, tree: Tree) -> None:
        """共通の処理."""
        raise NotImplementedError

    def s1(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def s2(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def s3(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def s4(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def s5(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def s6(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

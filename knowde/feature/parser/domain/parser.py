"""parser."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from lark import Lark, Transformer, Tree
from lark.indenter import Indenter
from lark.visitors import Visitor_Recursive

if TYPE_CHECKING:
    from lark.visitors import TransformerChain


class SampleIndenter(Indenter):
    """sample."""

    NL_type = "_NL"
    OPEN_PAREN_types = []  # noqa: RUF012
    CLOSE_PAREN_types = []  # noqa: RUF012
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


@cache
def common_parser(debug: bool = False) -> Lark:  # noqa: FBT001 FBT002
    """Lark Parser."""
    p = Path(__file__).parent / "input.lark"
    return Lark(
        p.read_text(),
        parser="lalr",
        debug=debug,
        postlex=SampleIndenter(),
    )


def transparse(
    text: str,
    t: Transformer | TransformerChain | None = None,
    debug: bool = False,  # noqa: FBT001 FBT002
) -> Tree:
    """Parse and transform."""
    txt = dedent(text)
    _tree = common_parser(debug=debug).parse(txt)
    if t is None:
        return _tree
    return t.transform(_tree)


class CommonVisitor(Visitor_Recursive, ABC):
    """共通ルール."""

    @abstractmethod
    def do(self, tree: Tree) -> None:
        """共通の処理."""
        raise NotImplementedError

    def h1(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def h2(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def h3(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def h4(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def h5(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

    def h6(self, tree: Tree) -> None:
        """For Rule."""
        self.do(tree)

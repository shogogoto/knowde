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


class ExampleIndenter(Indenter):
    """example."""

    NL_type = "_NL"
    OPEN_PAREN_types = []  # noqa: RUF012
    CLOSE_PAREN_types = []  # noqa: RUF012
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4

    # def handle_NL(self, token: Token) -> Iterator[Token]:
    #     print("-" * 80)
    #     print(f"tok='{token}'")
    #     if self.paren_level > 0:
    #         return

    #     yield token

    #     indent_str = token.rsplit("\n", 1)[1]  # Tabs and spaces
    #     indent = indent_str.count(" ") + indent_str.count("\t") * self.tab_len
    #     print(f"indent={indent}, str='{indent_str}'")
    #     if indent > self.indent_level[-1]:
    #         self.indent_level.append(indent)
    #         yield Token.new_borrow_pos(self.INDENT_type, indent_str, token)
    #     else:
    #         while indent < self.indent_level[-1]:
    #             self.indent_level.pop()
    #             yield Token.new_borrow_pos(self.DEDENT_type, indent_str, token)

    #         if indent != self.indent_level[-1]:
    #             msg = f"Unexpected dedent to column {indent}. Expected dedent to {self.indent_level[-1]}"  # noqa: E501
    #             raise DedentError(
    #                 msg,
    #             )


@cache
def common_parser(debug: bool = False) -> Lark:  # noqa: FBT001 FBT002
    """Lark Parser."""
    p = Path(__file__).parent / "input.lark"
    return Lark(
        p.read_text(),
        parser="lalr",
        # ambiguity="explicit",
        debug=debug,
        # postlex=PythonIndenter(),
        postlex=ExampleIndenter(),
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

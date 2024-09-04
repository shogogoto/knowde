"""textから章節を抜き出す."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from lark import Lark, ParseTree, Token, Transformer

# class IndentGrammer(Indenter):
#     pass


# class Heading(BaseModel):
#     value: str
#     children: list[Heading] = Field(default_factory=list)


# class Heading1(Heading):
#     children: list[Heading] = Field(default_factory=list)


# class Heading2(Heading):
#     pass


class TT(Transformer):
    """CST -> AST."""

    def H2(self, tok: Token) -> Any:  # noqa: ANN401 N802
        """Markdown H1."""
        # print(type(tok), tok)
        return tok.replace("#", "")


def parse(text: str) -> ParseTree:
    """Lark parser."""
    p = Path(__file__).parent / "input.lark"
    return Lark(
        p.read_text(),
        # ambiguity="explicit",
        parser="lalr",
        debug=True,
        transformer=TT(),
    ).parse(text)

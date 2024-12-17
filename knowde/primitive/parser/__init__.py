"""テキストから構文木作成."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from lark import Lark, Transformer, Tree, UnexpectedInput
from lark.indenter import Indenter

from knowde.primitive.parser.errors import HEAD_ERR_EXS

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


def parse2tree(
    text: str,
    transformer: TransformerChain | Transformer | None = None,
) -> Tree:
    """Parse and transform."""
    txt = dedent(text)
    parser = Lark(
        (Path(__file__).parent / "input.lark").read_text(),
        parser="lalr",
        postlex=SampleIndenter(),
        transformer=transformer,
    )
    try:
        return parser.parse(txt)  # , on_error=handle_error,
    except UnexpectedInput as e:
        exc_class = e.match_examples(
            parser.parse,
            HEAD_ERR_EXS,
            token_type_match_fallback=True,
        )
        if not exc_class:
            raise
        s = e.get_context(txt)
        raise exc_class(s, e.line, e.column) from e

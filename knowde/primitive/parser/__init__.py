"""テキストから構文木作成."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from lark import Lark, Transformer, Tree, UnexpectedInput
from lark.indenter import Indenter

from knowde.primitive.parser.errors import HEAD_ERR_EXS
from knowde.primitive.parser.transfomer import common_transformer

if TYPE_CHECKING:
    from lark.visitors import TransformerChain

# line_parser = Lark(
#     (Path(__file__).parent / "grammer/line.lark").read_text(),
#     parser="lalr",
# )


class SampleIndenter(Indenter):
    """sample."""

    NL_type = "_NL"
    OPEN_PAREN_types = []  # noqa: RUF012
    CLOSE_PAREN_types = []  # noqa: RUF012
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


def structure_parser(transformer: TransformerChain | Transformer | None = None) -> Lark:
    """lineパース以外."""
    return Lark(
        (Path(__file__).parent / "input.lark").read_text(),
        parser="lalr",
        postlex=SampleIndenter(),
        transformer=transformer,
    )


def parse2tree(text: str, do_transfrom: bool = False) -> Tree:  # noqa: FBT001 FBT002
    """Parse and transform."""
    txt = dedent(text)
    parser = structure_parser(
        transformer=common_transformer() if do_transfrom else None,
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

"""テキストから構文木作成."""
from __future__ import annotations

from functools import cache
from pathlib import Path
from textwrap import dedent

from lark import Lark, Tree, UnexpectedInput
from lark.indenter import Indenter

from knowde.primitive.parser.errors import HEAD_ERR_EXS


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
    p = Path(__file__).parent / "input2.lark"
    return Lark(
        p.read_text(),
        parser="lalr",
        debug=debug,
        postlex=SampleIndenter(),
    )


# def handle_error(e: UnexpectedToken) -> bool:
#     if e.token.type == "H3":
#         print("@" * 80)
#         print(e.token_history)
#     print("#" * 80)
#     print(e.token.type, e.token, f"line {e.line} col {e.column}")
#     print("#" * 80, "end")
#     return True


def parse2tree(
    text: str,
    debug: bool = False,  # noqa: FBT001 FBT002
) -> Tree:
    """Parse and transform."""
    txt = dedent(text)
    parser = common_parser(debug=debug)
    try:
        return parser.parse(
            txt,
            # on_error=handle_error,
        )
    except UnexpectedInput as e:
        exc_class = e.match_examples(
            parser.parse,
            HEAD_ERR_EXS,
            use_accepts=True,
        )
        if not exc_class:
            raise
        s = e.get_context(txt)
        raise exc_class(s, e.line, e.column) from e

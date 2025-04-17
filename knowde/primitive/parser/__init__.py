"""テキストから構文木作成."""

from __future__ import annotations

from collections.abc import Hashable
from functools import cache
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from lark import Lark, Transformer, Tree, UnexpectedInput
from lark.indenter import DedentError, Indenter

from knowde.primitive.parser.errors import HEAD_ERR_EXS, UndedentError
from knowde.primitive.parser.undent import detect_undent, front_pivot

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
def create_parser(transformer: TransformerChain | Transformer | None = None) -> Lark:
    """パーサ."""
    return Lark(
        (Path(__file__).parent / "input.lark").read_text(),
        parser="lalr",
        postlex=SampleIndenter(),
        transformer=transformer,
        # keep_all_token=True,
    )


def parse2tree(
    text: str,
    transformer: TransformerChain | Transformer | None = None,
) -> Tree:
    """Parse and transform."""
    txt = dedent(text)
    p = create_parser(transformer)
    try:
        return p.parse(txt)  # , on_error=handle_error)
    except UnexpectedInput as e:
        exc_class = e.match_examples(
            p.parse,
            HEAD_ERR_EXS,
            token_type_match_fallback=True,
        )
        if not exc_class:
            raise
        s = e.get_context(txt)
        raise exc_class(s, e.line, e.column) from e
    except DedentError as e:
        lines = txt.splitlines()
        pivot, w = front_pivot(len(lines), len(lines))
        i = detect_undent(create_parser().parse, lines, pivot, w)
        nums = range(i - 2, i + 2)
        digit = max(len(str(n)) for n in nums)
        arround = "\n".join([f"{n:>{digit}}: {lines[n]}" for n in nums])
        msg = f"Invalid indent was detected at line {i}. \n" + arround
        raise UndedentError(msg) from e


def get_leaves(tree: Tree) -> list[Hashable]:
    """leafを全て取得."""
    return list(tree.scan_values(lambda v: not isinstance(v, Tree)))

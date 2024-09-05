"""parser."""
from functools import cache
from pathlib import Path

from lark import Lark, Transformer


@cache
def common_parser(t: Transformer) -> Lark:
    """Lark Parser."""
    p = Path(__file__).parent / "input.lark"
    return Lark(
        p.read_text(),
        parser="lalr",
        transformer=t,
        # ambiguity="explicit",
        # debug=True,
    )

"""テキストから構文木作成."""
from __future__ import annotations

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


structure_parser = Lark(
    (Path(__file__).parent / "grammer/input2.lark").read_text(),
    parser="lalr",
    postlex=SampleIndenter(),
)

# line_parser = Lark(
#     (Path(__file__).parent / "grammer/line.lark").read_text(),
#     parser="lalr",
# )

ALIAS_SEP = "|"
DEF_SEP = ":"
NAME_SEP = ","


# larkでのparseが思ったようにいかなかったからあきらめた
#   aliasやname, sentenceで許容する文字列を思ったように設定できなかった
def parse_line(line: str) -> tuple[str | None, list[str], str | None]:
    """行を解析."""
    txt = dedent(line).strip()
    alias = None
    names = []
    define = txt
    sentence = txt
    if ALIAS_SEP in txt:
        alias, define = txt.split(ALIAS_SEP)
        alias = alias.strip()
        sentence = define
    if DEF_SEP in define:
        names, sentence = define.split(DEF_SEP)
        names = [n.strip() for n in names.split(NAME_SEP)]
    return alias, names, sentence.strip() if sentence else None


def parse2tree(text: str) -> Tree:
    """Parse and transform."""
    txt = dedent(text)
    parser = structure_parser
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

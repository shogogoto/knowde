"""行変換."""
from __future__ import annotations

from textwrap import dedent

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
        alias, define = txt.split(ALIAS_SEP, maxsplit=1)
        alias = alias.strip()
        sentence = define
    if DEF_SEP in define:
        names, sentence = define.split(DEF_SEP, 1)
        names = [n.strip() for n in names.split(NAME_SEP)]
    return alias, names, sentence.strip() if sentence else None

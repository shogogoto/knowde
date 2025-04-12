"""tree変換."""

from __future__ import annotations

from lark import Token, Transformer

from knowde.complex.__core__.sysnet.sysnode import Def, KNArg
from knowde.complex.__core__.tree2net.lineparse import parse_line
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.__core__.types import Duplicable
from knowde.primitive.template import Template
from knowde.primitive.term import Term
from knowde.primitive.time import WhenNode


def _stoken(tok: Token, erase: str | None = None) -> Token:
    """Strip token."""
    v = tok
    if erase:
        v = v.replace(erase, "")
    return Token(type=tok.type, value=v.strip())


class TSysArg(Transformer):
    """to SysArg transformer."""

    THUS = lambda _, _tok: EdgeType.TO.forward  # noqa: E731
    CAUSE = lambda _, _tok: EdgeType.TO.backward  # noqa: E731
    EXAMPLE = lambda _, _tok: EdgeType.EXAMPLE.forward  # noqa: E731
    GENERAL = lambda _, _tok: EdgeType.EXAMPLE.backward  # noqa: E731

    REF = lambda _, _tok: EdgeType.REF.forward  # noqa: E731
    WHEN = lambda _, _tok: EdgeType.WHEN.forward  # noqa: E731

    WHERE = lambda _, _tok: EdgeType.WHERE.forward  # noqa: E731
    BY = lambda _, _tok: EdgeType.BY.forward  # noqa: E731

    NUM = lambda _, _tok: EdgeType.NUM.forward  # noqa: E731

    ANTONYM = lambda _, _tok: EdgeType.ANTI.both  # noqa: E731
    SIMILAR = lambda _, _tok: EdgeType.SIMILAR.both  # noqa: E731
    DUPLICABLE = lambda _, _tok: Duplicable(n=_stoken(_tok))  # noqa: E731
    QUOTERM = lambda _, _tok: _stoken(_tok)  # noqa: E731
    TIME = lambda _, _tok: WhenNode.of(n=_stoken(_tok))  # noqa: E731

    # Resources
    AUTHOR = lambda _, _tok: _stoken(_tok, "@author")  # noqa: E731
    PUBLISHED = lambda _, _tok: _stoken(_tok, "@published")  # noqa: E731
    URL = lambda _, _tok: _stoken(_tok, "@url")  # noqa: E731

    @staticmethod
    def ONELINE(tok: Token) -> KNArg:  # noqa: N802 D102
        v = "".join(tok.split("   "))  # 適当な\nに対応する空白
        return _parse2sysarg(v)

    @staticmethod
    def MULTILINE(tok: Token) -> KNArg:  # noqa: N802 D102
        sp = tok.split("\\\n")
        v = ""
        for s in sp:
            v += s.lstrip()
        return _parse2sysarg(v)


def _parse2sysarg(v: str) -> KNArg:
    if Template.is_parsable(v):
        return Template.parse(v)

    alias, names, sentence = parse_line(v)
    if sentence is None:
        t = Term.create(*names, alias=alias)
        return Def.dummy(t)
    if alias is None and len(names) == 0:
        return sentence
    return Def.create(sentence, names, alias)

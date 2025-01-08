"""tree変換."""


from lark import Token, Transformer

from knowde.complex.__core__.sysnet.sysnode import Def, Duplicable, SysArg
from knowde.primitive.__core__.nxutil import EdgeType
from knowde.primitive.parser.lineparse import parse_line
from knowde.primitive.term import Term


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
    DUPLICABLE = lambda _, _tok: Duplicable(n=_tok.strip())  # noqa: E731
    QUOTERM = lambda _, _tok: Token(type=_tok.type, value=_tok.strip())  # noqa: E731

    def ONELINE(self, tok: Token) -> SysArg:  # noqa: N802 D102
        v = "".join(tok.split("   "))  # 適当な\nに対応する空白
        alias, names, sentence = parse_line(v)
        if sentence is None:
            t = Term.create(*names, alias=alias)
            return Def.dummy(t)
        if alias is None and len(names) == 0:
            return sentence
        return Def.create(sentence, names, alias)

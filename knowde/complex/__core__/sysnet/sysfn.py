"""sys系関数."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from lark import Token

from knowde.complex.__core__.sysnet.errors import SysNetNotFoundError
from knowde.complex.__core__.sysnet.sysnode import (
    Def,
    DummySentence,
    Duplicable,
    SysArg,
    SysNode,
)
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.term import Term

if TYPE_CHECKING:
    import networkx as nx


def to_term(vs: Iterable[SysArg]) -> list[Term]:
    """termのみを取り出す."""
    return [v.term for v in vs if isinstance(v, Def)]


def to_quoterm(vs: Iterable[SysArg]) -> list[Token]:
    """termのみを取り出す."""
    return [v for v in vs if isinstance(v, Token) and v.type == "QUOTERM"]


def to_sentence(vs: Iterable[SysArg]) -> list[str | DummySentence]:
    """文のみを取り出す."""
    defed = [v.sentence for v in vs if isinstance(v, Def)]
    return [*defed, *[v for v in vs if isinstance(v, (str, Duplicable))]]


def to_def(vs: Iterable[SysArg]) -> list[Def]:
    """文のみを取り出す."""
    return [v for v in vs if isinstance(v, Def)]


def get_ifdef(g: nx.DiGraph, n: SysNode) -> SysArg:
    """defがあれば返す."""
    if n not in g:
        msg = f"{n} is not in this graph."
        raise SysNetNotFoundError(msg)
    match n:
        case str() | Duplicable():
            term = EdgeType.DEF.get_pred_or_none(g, n)
            if term is None:
                return n
            return Def(term=term, sentence=n)
        case Term():
            s = EdgeType.DEF.get_succ_or_none(g, n)
            if s is None:
                return n
            return Def(term=n, sentence=s)
        case _:
            raise TypeError(n)

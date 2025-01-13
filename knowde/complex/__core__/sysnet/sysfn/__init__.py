"""sys系関数."""
from __future__ import annotations

from typing import TYPE_CHECKING, Hashable, Iterable

from lark import Token

from knowde.complex.__core__.sysnet.errors import (
    SysNetNotFoundError,
    sentence_dup_checker,
)
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


def to_term(vs: Iterable[Hashable]) -> list[Term]:
    """termのみを取り出す."""
    terms = [n for n in vs if isinstance(n, Term)]
    return [*terms, *[v.term for v in vs if isinstance(v, Def)]]


def to_quoterm(vs: Iterable[SysArg]) -> list[Token]:
    """termのみを取り出す."""
    return [v for v in vs if isinstance(v, Token) and v.type == "QUOTERM"]


def node2sentence(n: SysArg) -> str | DummySentence:
    """関係のハブとなる文へ."""
    match n:
        case Term():
            d = Def.dummy(n)
            return d.sentence
        case str() | Duplicable():
            return n
        case Def():
            return n.sentence
        case _:
            msg = f"{type(n)}: {n} is not allowed."
            raise TypeError(msg)


def to_sentence(vs: Iterable[Hashable]) -> list[str | DummySentence]:
    """文のみを取り出す."""
    defed = [v.sentence for v in vs if isinstance(v, Def)]
    return [*defed, *[v for v in vs if isinstance(v, (str, Duplicable))]]


def check_duplicated_sentence(vs: Iterable[Hashable]) -> None:
    """文の重複チェック."""
    s_chk = sentence_dup_checker()
    for s in to_sentence(vs):
        if isinstance(s, (DummySentence, Duplicable)):
            continue
        if isinstance(s, Token) and s.type == "QUOTERM":
            continue
        s_chk(s)


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

"""sys系関数."""
from __future__ import annotations

import re
from collections.abc import Hashable, Iterable
from typing import TYPE_CHECKING

from lark import Token

from knowde.complex.__core__.sysnet.errors import (
    SysNetNotFoundError,
    sentence_dup_checker,
)
from knowde.complex.__core__.sysnet.sysnode import (
    Def,
    DummySentence,
    KNArg,
    KNode,
)
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.__core__.types import Duplicable
from knowde.primitive.template import Template
from knowde.primitive.term import Term

if TYPE_CHECKING:
    import networkx as nx


def to_template(vs: Iterable[Hashable]) -> list[Template]:
    """テンプレートのみを取り出す."""
    return [v for v in vs if isinstance(v, Template)]


def to_term(vs: Iterable[Hashable]) -> list[Term]:
    """termのみを取り出す."""
    terms = [n for n in vs if isinstance(n, Term)]
    return [*terms, *[v.term for v in vs if isinstance(v, Def)]]


def to_quoterm(vs: Iterable[KNArg]) -> list[Token]:
    """termのみを取り出す."""
    return [v for v in vs if isinstance(v, Token) and v.type == "QUOTERM"]


def arg2sentence(n: KNArg) -> str | DummySentence:
    """関係のハブとなる文へ."""
    match n:
        case Template():
            return n
        # case Term():
        #     d = Def.dummy(n)
        #     return d.sentence
        case str() | Duplicable():
            return n
        case Def():
            return n.sentence
        case _:
            msg = f"{type(n)}: {n} is not allowed."
            raise TypeError(msg)


def to_sentence(vs: Iterable[Hashable]) -> list[str | Duplicable]:
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


def to_def(vs: Iterable[KNArg]) -> list[Def]:
    """文のみを取り出す."""
    return [v for v in vs if isinstance(v, Def)]


def get_ifdef(g: nx.DiGraph, n: KNode) -> KNArg:
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


QUOTERM_PETTERN = re.compile(r"^`.*`$")


def is_enclosed_in_backticks(s: str) -> bool:
    """引用用語 or not."""
    return bool(QUOTERM_PETTERN.match(s))


def get_ifquote(g: nx.DiGraph, n: KNArg) -> KNArg:
    """引用用語ならdefを返す."""
    if isinstance(n, str) and is_enclosed_in_backticks(n):
        succ = EdgeType.QUOTERM.get_succ_or_none(g, n)
        if succ is None:
            raise TypeError
        return get_ifdef(g, succ)
    return None

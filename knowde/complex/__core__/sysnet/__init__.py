"""系ネットワーク."""
from __future__ import annotations

import networkx as nx
from pydantic import BaseModel, Field

from knowde.primitive.__core__.nxutil import (
    EdgeType,
    to_nested,
)
from knowde.primitive.__core__.types import NXGraph
from knowde.primitive.heading import get_headings
from knowde.primitive.term import Term

from .errors import (
    SysNetNotFoundError,
)
from .sysnode import Def, Duplicable, SysArg, SysNode


class SysNet(BaseModel, frozen=True):
    """系ネットワーク."""

    root: str
    g: NXGraph = Field(default_factory=nx.MultiDiGraph)

    def get(self, n: SysNode) -> SysArg:
        """文に紐づく用語があれば定義を返す."""
        if n not in self.g:
            msg = f"{n} is not in system[{self.root}]."
            raise SysNetNotFoundError(msg)
        # return get_ifdef(self.g, n)
        match n:
            case str() | Duplicable():
                term = EdgeType.DEF.get_pred_or_none(self.g, n)
                if term is None:
                    return n
                return Def(term=term, sentence=n)
            case Term():
                s = EdgeType.DEF.get_succ_or_none(self.g, n)
                if s is None:
                    return n
                return Def(term=n, sentence=s)
            case _:
                raise TypeError

    @property
    def sentences(self) -> list[str]:
        """文."""
        hs = get_headings(self.g, self.root)
        return [
            n for n in self.g.nodes if isinstance(n, (str, Duplicable)) and n not in hs
        ]

    @property
    def terms(self) -> list[Term]:
        """用語."""
        return [n for n in self.g.nodes if isinstance(n, Term)]

    def get_resolved(self, s: str) -> dict:
        """解決済み入れ子文を取得."""
        return to_nested(self.g, s, EdgeType.RESOLVED.succ)

"""系ネットワーク."""
from __future__ import annotations

from functools import cached_property

import networkx as nx
from pydantic import BaseModel, Field

from knowde.complex.__core__.sysnet.sysfn import (
    get_ifdef,
    get_ifquote,
    to_sentence,
    to_template,
    to_term,
)
from knowde.primitive.__core__.nxutil import EdgeType, to_nested
from knowde.primitive.__core__.types import NXGraph
from knowde.primitive.heading import get_headings
from knowde.primitive.template import Templates
from knowde.primitive.term import Term

from .errors import SysNetNotFoundError
from .sysnode import Def, Duplicable, SysArg, SysNode


class SysNet(BaseModel, frozen=True):
    """系ネットワーク."""

    root: str
    g: NXGraph = Field(default_factory=nx.MultiDiGraph)

    def get(self, n: SysNode) -> SysArg:
        """文に紐づく用語があれば定義を返す."""
        self.check_contains(n)
        q = get_ifquote(self.g, n)
        return q or get_ifdef(self.g, n)

    @cached_property
    def sentences(self) -> list[str | Duplicable]:
        """文."""
        stc = to_sentence(self.g.nodes)
        hs = get_headings(self.g, self.root)
        return [n for n in stc if n not in hs]

    @cached_property
    def terms(self) -> list[Term]:
        """用語."""
        return to_term(self.g.nodes)

    def get_resolved(self, s: str) -> dict:
        """解決済み入れ子文を取得."""
        return to_nested(self.g, s, EdgeType.RESOLVED.succ)

    @cached_property
    def sentence_graph(self) -> nx.DiGraph:
        """文のみのGraph."""
        return nx.subgraph(self.g, [s for s in self.sentences if isinstance(s, str)])

    @cached_property
    def _templates(self) -> Templates:
        """テンプレートの集まり."""
        return Templates().add(*to_template(self.g.nodes))

    def expand(self, n: SysNode) -> SysArg:
        """テンプレを展開."""
        got = self.get(n)
        ts = self._templates
        match got:
            case str():
                return ts.expand(got)
            case Duplicable():
                return ts.expand(str(n))
            case Def():
                return Def(term=got.term, sentence=ts.expand(str(got.sentence)))
            case _:
                raise TypeError(n)

    def match(self, pattern: str) -> list[str | Duplicable]:
        """部分一致したものを返す."""
        gots = [self.get(n) for n in self.g.nodes if pattern in str(n)]
        return [e.sentence if isinstance(e, Def) else e for e in gots]

    def check_contains(self, n: SysNode) -> None:
        """含なければエラー."""
        if n not in self.g:
            msg = f"{n} is not in system[{self.root}]."
            raise SysNetNotFoundError(msg)

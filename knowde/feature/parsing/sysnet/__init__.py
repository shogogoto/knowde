"""系ネットワーク."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import networkx as nx
from lark import Token
from pydantic import BaseModel

from knowde.feature.parsing.primitive.heading import get_headings
from knowde.feature.parsing.primitive.template import Templates
from knowde.feature.parsing.primitive.time import Series, WhenNode
from knowde.feature.parsing.sysnet.sysfn import (
    get_ifdef,
    get_ifquote,
    to_sentence,
    to_template,
    to_term,
)
from knowde.shared.nxutil import to_nested
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import Duplicable, NXGraph

from .errors import SysNetNotFoundError
from .sysnode import Def, KNArg, KNode, is_meta

if TYPE_CHECKING:
    from knowde.feature.parsing.primitive.term import Term


# 様々なgetter機能を分離したいかも
class SysNet(BaseModel, frozen=True):
    """系ネットワーク."""

    root: str
    g: NXGraph

    def get(self, n: KNode) -> KNArg:
        """文に紐づく用語があれば定義を返す."""
        self.check_contains(n)
        q = get_ifquote(self.g, n)
        return q or get_ifdef(self.g, n)

    @cached_property
    def sentences(self) -> list[str | Duplicable]:
        """文."""
        stc = to_sentence(self.g.nodes)
        hs = get_headings(self.g, self.root)
        stc = [n for n in stc if n not in hs]
        return [s for s in stc if not is_meta(s)]

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

    def expand(self, n: KNode) -> KNArg:
        """テンプレを展開(viewのときにのみ使うことを想定)."""
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
        return list({e.sentence if isinstance(e, Def) else e for e in gots})

    def check_contains(self, n: KNode) -> None:
        """含なければエラー."""
        if n not in self.g:
            msg = f"{n} is not in system[{self.root}]."
            raise SysNetNotFoundError(msg)

    @cached_property
    def whens(self) -> list[WhenNode]:
        """WhenNodeのリスト."""
        return [n for n in self.g.nodes if isinstance(n, WhenNode)]

    @cached_property
    def series(self) -> Series:
        """時系列一覧."""
        whens = []
        for _u, v, d in self.g.edges(data=True):
            if d["type"] == EdgeType.WHEN:
                whens.append(v)
        return Series.create(whens)

    @cached_property
    def meta(self) -> list[Token]:
        """メタ情報."""
        return [
            n
            for n in self.g.nodes
            if isinstance(n, Token) and n.type in {"AUTHOR", "URL", "PUBLISHED"}
        ]

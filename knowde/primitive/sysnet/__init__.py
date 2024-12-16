"""系ネットワーク."""
from __future__ import annotations

from typing import Any, Hashable

from networkx import DiGraph
from pydantic import BaseModel, Field, PrivateAttr

from knowde.core.nxutil import (
    EdgeType,
)
from knowde.core.types import NXGraph
from knowde.primitive.heading import get_headings
from knowde.primitive.term import MergedTerms, Term, resolve_sentence

from .errors import SysNetNotFoundError, UnResolvedTermError
from .sysnode import Def, SysArg, SysNode


class SysNet(BaseModel):
    """系ネットワーク."""

    root: str
    g: NXGraph = Field(default_factory=DiGraph, init=False)
    _is_resolved: bool = PrivateAttr(default=False)

    def model_post_init(self, __context: Any) -> None:  # noqa: ANN401 D102
        self.g.add_node(self.root)

    def add(self, t: EdgeType, *path: SysArg) -> tuple[SysArg, ...]:
        """既存nodeから開始していない場合はrootからedgeを伸ばすように登録."""
        if len(path) > 0:
            first = path[0]
            _p = path if first in self.g else [self.root, *path]
            t.add_path(self.g, *_p, cvt=self._pre_add_edge)
        return path

    def _pre_add_edge(self, n: Hashable) -> Hashable:
        """定義の追加."""
        match n:
            case Term() | str():
                self.g.add_node(n)
                return n
            case Def():
                EdgeType.DEF.add_edge(self.g, n.term, n.sentence)
                return n.sentence
            case _:
                raise TypeError

    @property
    def sentences(self) -> list[str]:
        """文."""
        s = [n for n in self.g.nodes if isinstance(n, str)]
        [s.remove(h) for h in get_headings(self.g, self.root)]
        return s

    def add_resolved_edges(self) -> None:
        """事前の全用語解決.

        統計情報を得るためには、全て用語解決しとかないといけない
        DBやstageからは解決済みのnetworkを復元
        """
        terms = [n for n in self.g.nodes if isinstance(n, Term)]
        r = MergedTerms().add(*terms).to_resolver()
        r.add_edges(self.g, self.sentences)
        self._is_resolved = True

    def get_resolved(self, s: str) -> dict:
        """解決済み入れ子文を取得."""
        if not self._is_resolved:
            raise UnResolvedTermError
        return resolve_sentence(self.g, s)

    def get(self, n: SysNode) -> SysArg:
        """文に紐づく用語があれば定義を返す."""
        if n not in self.g:
            raise SysNetNotFoundError
        match n:
            case str():
                term = EdgeType.DEF.get_pred(self.g, n)
                if term is None:
                    return n
                return Def(term=term, sentence=n)
            case Term():
                s = EdgeType.DEF.get_succ(self.g, n)
                if s is None:
                    return n
                return Def(term=n, sentence=s)
            case _:
                raise TypeError

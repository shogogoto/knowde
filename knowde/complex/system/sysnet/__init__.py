"""系ネットワーク."""
from __future__ import annotations

from typing import Any, Hashable

from networkx import DiGraph
from pydantic import BaseModel, PrivateAttr

from knowde.complex.system.sysnet.errors import (
    SysNetNotFoundError,
    UnResolvedTermError,
)
from knowde.core.nxutil import (
    EdgeType,
)
from knowde.core.types import NXGraph
from knowde.primitive.heading import get_headings
from knowde.primitive.term import MergedTerms, Term, resolve_sentence

from .sysnode import Def, SysArg, SysNode, arg2node


class SysNet(BaseModel):
    """系ネットワーク."""

    root: str
    _g: NXGraph = PrivateAttr(default_factory=DiGraph, init=False)
    _is_resolved: bool = PrivateAttr(default=False)

    @property
    def graph(self) -> DiGraph:  # noqa: D102
        return self._g

    def model_post_init(self, __context: Any) -> None:  # noqa: ANN401 D102
        self._g.add_node(self.root)

    def add(self, t: EdgeType, *path: SysArg) -> list[SysArg]:
        """既存nodeから開始していない場合はrootからedgeを伸ばすように登録."""
        match len(path):
            case l if l == 1:
                n = self.add_new(path[0])
                return [n]
            case l if l >= 2:  # noqa: PLR2004
                f = self._check_added(path[0])
                ps = [f, *[self.add_new(p) for p in path[1:]]]
                return t.add_path(self._g, *ps)
            case _:
                return list(path)

    def _check_added(self, n: SysArg) -> SysNode:
        """追加済みのはず."""
        match n:
            case self.root:
                return n
            case Term() | str() | Def():
                return arg2node(n)
                # if n not in self._g.nodes:
                #     msg = f"'{n}'は追加されていません."
                #     raise UnaddedYetError(msg)
            case _:
                msg = f"{type(n)}: {n} is not allowed."
                raise TypeError(msg)

    def add_new(self, n: Hashable) -> SysNode:
        """新規追加."""
        match n:
            case self.root:
                return n
            case Term() | str():
                # if n in self._g.nodes:
                #     msg = f"{n}は予期せずに追加済みです"
                #     raise AlreadyAddedError(msg)
                self._g.add_node(n)
                return n
            case Def():
                # if (n.term, n.sentence) in self._g.edges:
                #     msg = f"定義{n}は予期せずに追加済みです"
                #     raise AlreadyAddedError(msg)
                EdgeType.DEF.add_edge(self._g, n.term, n.sentence)
                return n.sentence
            case _:
                msg = f"{type(n)}: {n} is not allowed."
                raise TypeError(msg)

    def get(self, n: SysNode) -> SysArg:
        """文に紐づく用語があれば定義を返す."""
        if n not in self._g:
            raise SysNetNotFoundError
        match n:
            case str():
                term = EdgeType.DEF.get_pred(self._g, n)
                if term is None:
                    return n
                return Def(term=term, sentence=n)
            case Term():
                s = EdgeType.DEF.get_succ(self._g, n)
                if s is None:
                    return n
                return Def(term=n, sentence=s)
            case _:
                raise TypeError

    @property
    def sentences(self) -> list[str]:
        """文."""
        hs = get_headings(self._g, self.root)
        return [n for n in self._g.nodes if isinstance(n, str) and n not in hs]

    def add_resolved_edges(self) -> None:
        """事前の全用語解決.

        統計情報を得るためには、全て用語解決しとかないといけない
        DBやstageからは解決済みのnetworkを復元
        """
        terms = [n for n in self._g.nodes if isinstance(n, Term)]
        r = MergedTerms().add(*terms).to_resolver()
        r.add_edges(self._g, self.sentences)
        self._is_resolved = True

    def get_resolved(self, s: str) -> dict:
        """解決済み入れ子文を取得."""
        if not self._is_resolved:
            raise UnResolvedTermError
        return resolve_sentence(self._g, s)

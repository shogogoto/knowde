"""系ネットワーク."""
from __future__ import annotations

from functools import cached_property
from itertools import pairwise
from typing import Any, Hashable

from lark import Token
from networkx import DiGraph
from pydantic import BaseModel, PrivateAttr

from knowde.complex.__core__.sysnet.dupchk import SysArgDupChecker
from knowde.primitive.__core__.nxutil import (
    EdgeType,
    replace_node,
)
from knowde.primitive.__core__.types import NXGraph
from knowde.primitive.heading import get_headings
from knowde.primitive.term import (
    MergedTerms,
    Term,
    TermResolver,
    resolve_sentence,
)

from .errors import (
    AlreadyAddedError,
    QuotermNotFoundError,
    SysNetNotFoundError,
    UnResolvedTermError,
)
from .sysnode import Def, SysArg, SysNode


class SysNet(BaseModel):
    """系ネットワーク."""

    root: str
    _g: NXGraph = PrivateAttr(default_factory=DiGraph, init=False)
    _chk: SysArgDupChecker = PrivateAttr(default_factory=SysArgDupChecker)
    _is_resolved: bool = PrivateAttr(default=False)

    @property
    def g(self) -> DiGraph:  # noqa: D102
        return self._g

    def model_post_init(self, __context: Any) -> None:  # noqa: ANN401 D102
        self._g.add_node(self.root)
        self._chk(self.root)

    def add(self, t: EdgeType, *path: SysArg) -> None:
        """既存nodeから開始していない場合はrootからedgeを伸ばすように登録."""
        match len(path):
            case l if l == 1:
                n = path[0]
                self._chk(n)
                self.add_arg(n)
            case l if l >= 2:  # noqa: PLR2004
                for u, v in pairwise(path):
                    self.add_new_edge(t, u, v)
            case _:
                pass

    def add_new_edge(self, t: EdgeType, u: SysArg, v: SysArg) -> None:
        """追加済みのはず."""
        un = self.add_arg(u)
        vn = self.add_arg(v)
        if (un, vn, {"type": t}) in self._g.edges.data():
            msg = f"{u}-[{t}]->{v}は重複追加です"
            raise AlreadyAddedError(msg)
        t.add_edge(self._g, un, vn)

    def add_arg(self, n: Hashable) -> SysNode:
        """新規追加."""
        match n:
            case Term() | str():
                self._g.add_node(n)
                return n
            case Def():
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
                term = EdgeType.DEF.get_pred_or_none(self._g, n)
                if term is None:
                    return n
                return Def(term=term, sentence=n)
            case Term():
                s = EdgeType.DEF.get_succ_or_none(self._g, n)
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

    @property
    def terms(self) -> list[Term]:
        """用語."""
        return [n for n in self._g.nodes if isinstance(n, Term)]

    ################################################# 用語解決
    @cached_property
    def resolver(self) -> TermResolver:  # noqa: D102
        return MergedTerms().add(*self.terms).to_resolver()

    def add_resolved_edges(self) -> None:
        """事前の全用語解決.

        統計情報を得るためには、全て用語解決しとかないといけない
        DBやstageからは解決済みのnetworkを復元
        """
        self.resolver.add_edges(self._g, self.sentences)
        # self._g = nx.freeze(self._g)
        self._is_resolved = True

    def get_resolved(self, s: str) -> dict:
        """解決済み入れ子文を取得."""
        if not self._is_resolved:
            raise UnResolvedTermError
        return resolve_sentence(self._g, s)

    ################################################# 引用用語置換
    @property
    def quoterms(self) -> list[str]:
        """引用用語."""
        return [
            n for n in self._g.nodes if isinstance(n, Token) and n.type == "QUOTERM"
        ]

    def replace_quoterms(self) -> None:
        """引用用語を1文に置換."""
        for qt in self.quoterms:
            name = qt.replace("`", "")
            if name not in self.resolver.lookup:
                msg = f"'{name}'は用語として定義されていません"
                raise QuotermNotFoundError(msg)
            term = self.resolver.lookup[name]
            d = self.get(term)
            if isinstance(d, Def):
                replace_node(self._g, qt, d.sentence)
            else:
                raise TypeError

"""ツリーの重複チェック."""
from __future__ import annotations

from typing import Self

import networkx as nx
from lark import Token, Tree
from pydantic import Field
from typing_extensions import override

from knowde.complex.__core__.sysnet.adder import add_def
from knowde.complex.__core__.sysnet.sysnode import (
    Def,
    DummySentence,
    Duplicable,
    IDef,
    SysArg,
)
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.__core__.util import parted
from knowde.primitive.term import MergedTerms, Term

from .errors import sentence_dup_checker


def extract_leaves(tree: Tree) -> tuple[MergedTerms, nx.DiGraph]:
    """transformedなASTを処理."""
    leaves = get_leaves(tree)
    mt = check_and_merge_term(leaves)
    # md = MergedDef.create(mt, to_def(leaves))
    dg = to_def_graph(leaves)
    return mt, dg


def check_and_merge_term(leaves: list[SysArg]) -> MergedTerms:
    """重複チェック."""
    mt = MergedTerms().add(*to_term(leaves))
    s_chk = sentence_dup_checker()
    for s in to_sentence(leaves):
        if isinstance(s, DummySentence):
            continue
        s_chk(s)
    return mt


class MergedDef(IDef, frozen=True):
    """termのマージによって生成されるまとめられたDef."""

    term: Term
    sentences: list[str] = Field(min_length=1)

    @override
    def __str__(self) -> str:
        return f"{self.term}: {self.sentences}"

    @classmethod
    def one(cls, t: Term, *sentences: str) -> Self:
        """Create instance."""
        return cls(term=t, sentences=list(sentences))

    @classmethod
    def create(cls, mt: MergedTerms, defs: list[Def]) -> tuple[list[Self], list[Def]]:
        """Batch create."""
        other = defs

        def _will_merge(t: Term, d: Def) -> bool:
            return t.allows_merge(d.term) or t == d.term

        ls = []
        remain = []
        for t in mt.frozen:
            tgt, other = parted(other, lambda d: _will_merge(t, d))  # noqa: B023
            if len(tgt) == 1:  # マージ不要
                remain.extend(tgt)
                continue
            stcs = [
                d.sentence for d in tgt if not isinstance(d.sentence, DummySentence)
            ]
            ls.append(cls.one(t, *stcs))
        return ls, remain

    @override
    def add_edge(self, g: nx.DiGraph) -> None:
        """edgeの追加."""
        d = Def(term=self.term, sentence=self.sentences[0])
        d.add_edge(g)
        subs = self.sentences[1:]
        if len(subs) >= 1:
            EdgeType.BELOW.add_path(g, d.sentence, subs[0])
            EdgeType.SIBLING.add_path(g, *subs)


def get_leaves(tree: Tree) -> list[SysArg]:
    """leafを全て取得."""
    return list(tree.scan_values(lambda v: not isinstance(v, Tree)))


def is_quoterm(v: SysArg) -> bool:
    """filter用."""
    return isinstance(v, Token) and v.type == "QUOTERM"


def is_duplicable(v: SysArg) -> bool:
    """filter用."""
    return isinstance(v, Duplicable)


def to_term(vs: list[SysArg]) -> list[Term]:
    """termのみを取り出す."""
    return [v.term for v in vs if isinstance(v, Def)]


def to_sentence(vs: list[SysArg]) -> list[str | DummySentence]:
    """文のみを取り出す."""
    defed = [v.sentence for v in vs if isinstance(v, Def)]
    return [*defed, *[v for v in vs if isinstance(v, str)]]


def to_def(vs: list[SysArg]) -> list[Def]:
    """文のみを取り出す."""
    return [v for v in vs if isinstance(v, Def)]


def to_def_graph(vs: list[SysArg]) -> nx.MultiDiGraph:
    """defのみを取り出す."""
    dg = nx.MultiDiGraph()
    defs = [v for v in vs if isinstance(v, Def)]
    for _def in defs:
        add_def(dg, _def)
    return dg

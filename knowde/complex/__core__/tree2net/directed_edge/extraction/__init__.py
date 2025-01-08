"""ツリーの重複チェック."""
from __future__ import annotations

from typing import Self

import networkx as nx
from lark import Tree
from pydantic import Field
from typing_extensions import override

from knowde.complex.__core__.sysnet.sysfn import to_def, to_sentence, to_term
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
from knowde.primitive.term.markresolver import MarkResolver

from .errors import sentence_dup_checker


def extract_leaves(tree: Tree) -> tuple[nx.MultiDiGraph, MarkResolver]:
    """transformedなASTを処理."""
    leaves = get_leaves(tree)
    mt = check_and_merge_term(leaves)
    mdefs, stddefs = MergedDef.create(mt, to_def(leaves))
    g = nx.MultiDiGraph()
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]
    return g, MarkResolver.create(mt)


def check_and_merge_term(leaves: list[SysArg]) -> MergedTerms:
    """重複チェック."""
    mt = MergedTerms().add(*to_term(leaves))
    s_chk = sentence_dup_checker()
    for s in to_sentence(leaves):
        if isinstance(s, (DummySentence, Duplicable)):
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

        def _will_merge(t: Term, d: Def) -> bool:
            return t.allows_merge(d.term) or t == d.term

        ls = []
        remain = []
        other = defs
        for t in mt.frozen:
            tgt, other = parted(other, lambda d: _will_merge(t, d))  # noqa: B023
            if len(tgt) == 1:  # マージ不要
                remain.extend(tgt)
                continue
            stcs = [d.sentence for d in tgt if not d.is_dummy]
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

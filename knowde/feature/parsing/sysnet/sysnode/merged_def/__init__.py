"""ツリーの重複チェック."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

from pydantic import Field

from knowde.feature.parsing.primitive.term import (
    MergedTerms,
    Term,
    check_and_merge_term,
    eq_term,
)
from knowde.feature.parsing.sysnet.sysnode import Def, IDef
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.util import parted

if TYPE_CHECKING:
    import networkx as nx


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
    def create_and_parted(
        cls,
        defs: list[Def],
    ) -> tuple[list[Self], list[Def], MergedTerms]:
        """Batch create."""
        mt = check_and_merge_term([d.term for d in defs])

        def _will_merge(t: Term, d: Def) -> bool:
            t_ = d.term
            return t.allows_merge(t_) or eq_term(t, t_) or (t.has(*t_.names))

        merged = []
        std = []  # 普通のDef
        other = defs
        for t in mt.frozen:
            tgt, other = parted(other, lambda d: _will_merge(t, d))  # noqa: B023
            if len(tgt) <= 1:  # マージ不要
                std.extend(tgt)
                continue
            stcs = [d.sentence for d in tgt if not d.is_dummy]
            merged.append(cls.one(t, *stcs))
        return merged, std, mt

    @override
    def add_edge(self, g: nx.DiGraph) -> None:
        """edgeの追加."""
        d = Def(term=self.term, sentence=self.sentences[0])
        d.add_edge(g)
        subs = self.sentences[1:]
        if len(subs) >= 1:
            EdgeType.BELOW.add_path(g, d.sentence, subs[0])
            EdgeType.SIBLING.add_path(g, *subs)

"""ツリーの重複チェック."""
from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import Field
from typing_extensions import override

from knowde.complex.__core__.sysnet.sysnode import Def, IDef
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.__core__.util import parted
from knowde.primitive.term import MergedTerms, Term, eq_term

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
    def create(cls, mt: MergedTerms, defs: list[Def]) -> tuple[list[Self], list[Def]]:
        """Batch create."""

        def _will_merge(t: Term, d: Def) -> bool:
            t_ = d.term
            return t.allows_merge(t_) or eq_term(t, t_)

        ls = []
        remain = []
        other = defs
        for t in mt.frozen:
            tgt, other = parted(other, lambda d: _will_merge(t, d))  # noqa: B023
            if len(tgt) <= 1:  # マージ不要
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

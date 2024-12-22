"""定義ドメインモデル.

用語(rm(value=v).value

    @field_validator("explain")
    def _valid_explain(cls, v: str) -> str:
        return Sentence(value=v).value

"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID  # noqa: TCH003

import networkx as nx
from pydantic import BaseModel, Field, field_validator

from knowde.complex.definition.domain.description import PlaceHeldDescription
from knowde.complex.definition.repo.mark import RelMark
from knowde.complex.definition.sentence.domain import Sentence, SentenceParam
from knowde.complex.definition.term.domain import Term, TermParam
from knowde.primitive.__core__.domain import Composite, Entity
from knowde.primitive.__core__.types import NXGraph

if TYPE_CHECKING:
    from knowde.primitive.__core__.label_repo.base import RelBase


class DefinitionParam(BaseModel, frozen=True):
    """定義パラメータ."""

    name: str
    explain: str

    @field_validator("name")
    def _valid_name(cls, v: str) -> str:
        return TermParam(value=v).value

    @field_validator("explain")
    def _valid_explain(cls, v: str) -> str:
        return SentenceParam(value=v).value


class Definition(Entity, frozen=True):
    """定義モデル."""

    term: Term
    sentence: Sentence
    deps: list[Term] = Field(default_factory=list)

    @property
    def name(self) -> str:
        """term.value alias."""
        return self.term.value

    @property
    def explain(self) -> str:
        """Description sentence alias."""
        d = PlaceHeldDescription(value=self.sentence.value)
        vals = [v.value for v in self.deps]
        return d.inject(vals).value

    @property
    def output(self) -> str:
        """1行のテキスト表現."""
        s = self.updated.strftime("%y/%m/%d")
        return f"{s} {self.name}: {self.explain} ({self.valid_uid})"

    @classmethod
    def from_rel(
        cls,
        rel: RelBase,
        deps: Optional[list[Term]] = None,
    ) -> Self:
        """Create from Relationship."""
        if deps is None:
            deps = []
        t = Term.to_model(rel.start_node())
        s = Sentence.to_model(rel.end_node())
        return cls(
            term=t,
            sentence=s,
            deps=deps,
            uid=rel.uid,
            created=rel.created,
            updated=rel.updated,
        )


class DefinitionTree(BaseModel, frozen=True):
    """定義文章に依存する定義."""

    root_term_uid: UUID
    g: NXGraph

    @property
    def rootdef(self) -> Definition:
        """rootの定義."""
        return self.get_definition(self._root_term)

    def get_definition(self, term: Term) -> Definition:
        """Create definition by term model."""
        attrs = nx.get_edge_attributes(self.g, "rel")
        sentence = next(self.g.successors(term))
        rel = attrs[term, sentence]
        return Definition.from_rel(rel, self._marked_terms(sentence))

    def get_children(self, d: Definition) -> list[Definition]:
        """定義に使用された定義一覧."""
        return [
            self.get_definition(t)
            for t in self._marked_terms(
                d.sentence,
            )
        ]

    def build(self) -> Composite[Definition]:
        """Return recursive definition."""
        return self._build(self._root_term)

    @property
    def _root_term(self) -> Term:
        """rootの文章."""
        return next(filter(lambda n: n.valid_uid == self.root_term_uid, self.g.nodes))

    def _build(self, term: Term) -> Composite[Definition]:
        p = self.get_definition(term)
        children = [self._build(t) for t in self._marked_terms(p.sentence)]
        return Composite[Definition](
            parent=p,
            children=children,
        )

    def _marked_terms(self, sentence: Sentence) -> list[Term]:
        attrs = nx.get_edge_attributes(self.g, "rel")
        rels = [attrs[sentence, term] for term in self.g.successors(sentence)]
        return RelMark.sort(rels)

"""定義ドメインモデル.

用語(rm(value=v).value

    @field_validator("explain")
    def _valid_explain(cls, v: str) -> str:
        return Sentence(value=v).value

"""
from __future__ import annotations

from abc import ABC, abstractmethod
from textwrap import indent
from uuid import UUID  # noqa: TCH003

import networkx as nx
from pydantic import BaseModel, Field, field_validator
from typing_extensions import override

from knowde._feature._shared.domain import DomainModel
from knowde._feature.sentence.domain import Sentence, SentenceParam
from knowde._feature.term.domain import Term, TermParam
from knowde.feature.definition.domain.description import PlaceHeldDescription
from knowde.feature.definition.repo.mark import RelMark


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


class OutputProtocol(ABC):
    """oneline string output interface."""

    @property
    @abstractmethod
    def output(self) -> str:
        """Output oneline string for printing."""
        raise NotImplementedError


class Definition(DomainModel, OutputProtocol, frozen=True):
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
    @override
    def output(self) -> str:
        """1行のテキスト表現."""
        return f"{self.name}: {self.explain} ({self.valid_uid})"


class DefinitionComposite(
    BaseModel,
    OutputProtocol,
    frozen=True,
    arbitrary_types_allowed=True,
):
    """入れ子定義."""

    parent: Definition
    children: list[DefinitionComposite] = Field(default_factory=list)

    @property
    @override
    def output(self) -> str:
        """複数行のテキスト表現."""
        txt = self.parent.output
        for c in self.children:
            txt += "\n" + indent(c.output, " " * 2)
        return txt


class DefinitionTree(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    """定義文章に依存する定義."""

    root_term_uid: UUID
    g: nx.DiGraph

    @property
    def root(self) -> Term:
        """rootの文章."""
        return next(filter(lambda n: n.valid_uid == self.root_term_uid, self.g.nodes))

    @property
    def rootdef(self) -> Definition:
        """rootの定義."""
        return self.get_definition(self.root)

    def get_definition(self, term: Term) -> Definition:
        """Create definition by term model."""
        attrs = nx.get_edge_attributes(self.g, "rel")
        sentence = next(self.g.successors(term))
        drel = attrs[term, sentence]
        return Definition(
            term=term,
            sentence=sentence,
            deps=self._marked_terms(sentence),
            uid=drel.uid,
            created=drel.created,
            updated=drel.updated,
        )

    def get_children(self, d: Definition) -> list[Definition]:
        """定義に使用された定義一覧."""
        return [
            self.get_definition(t)
            for t in self._marked_terms(
                d.sentence,
            )
        ]

    def build(self) -> DefinitionComposite:
        """Return recursive definition."""
        return self._build(self.root)

    def _build(self, term: Term) -> DefinitionComposite:
        p = self.get_definition(term)
        children = [self._build(t) for t in self._marked_terms(p.sentence)]
        return DefinitionComposite(
            parent=p,
            children=children,
        )

    def _marked_terms(self, sentence: Sentence) -> list[Term]:
        attrs = nx.get_edge_attributes(self.g, "rel")
        rels = [attrs[sentence, term] for term in self.g.successors(sentence)]
        return RelMark.sort(rels)

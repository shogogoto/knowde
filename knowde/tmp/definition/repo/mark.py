"""説明文の依存関係解決.

(:Sentence)-[:MARK]->(:Term)-[:DEFINE]->(:Sentence)
"""

from __future__ import annotations

from operator import attrgetter
from typing import TYPE_CHECKING, Self

from neomodel import IntegerProperty
from pydantic import BaseModel, Field

from knowde.primitive.__core__ import RelBase, RelUtil
from knowde.tmp.definition.domain.mark import (
    inject2placeholder,
)
from knowde.tmp.definition.repo.errors import UndefinedMarkedTermError
from knowde.tmp.definition.sentence import LSentence2, SentenceUtil
from knowde.tmp.definition.term import LTerm2, TermUtil
from knowde.tmp.definition.term.domain import Term

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.primitive.__core__.label_repo.label import Label
    from knowde.tmp.definition.domain.description import (
        Description,
    )
    from knowde.tmp.definition.sentence.domain import Sentence


class RelMark(RelBase):
    """Mark Relationship with order."""

    order = IntegerProperty()

    @classmethod
    def sort(cls, ls: list[Self]) -> list[Term]:
        """Sort by order."""
        rels = sorted(ls, key=attrgetter("order"))
        return [Term.to_model(rel.end_node()) for rel in rels]


RelMarkUtil = RelUtil(
    t_source=LSentence2,
    t_target=LTerm2,
    name="MARK",
    t_rel=RelMark,
)


class ReturnMarkedDescription(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    """marked sentence with terms."""

    # Label[LSentence, Sentence]だとValidationErrorになる
    label: LSentence2
    model: Sentence
    terms: list[Term] = Field(default_factory=list)

    def to_model(self) -> Sentence:
        """To model."""
        return self.model


def add_description(d: Description) -> ReturnMarkedDescription:
    """markを解決して永続化."""
    s = SentenceUtil.find_one_or_none(value=d.value)
    if s is None:
        s = SentenceUtil.create(value=d.placeheld.value)
    rels = []
    for i, mv in enumerate(d.markvalues):
        t = TermUtil.find_one_or_none(value=mv.value)
        if t is None:
            msg = f"用語'{mv.value}'は見つかりませんでした'"
            raise UndefinedMarkedTermError(msg)
        rel = RelMarkUtil.connect(s.label, t.label, order=i)
        rels.append(rel)
    return ReturnMarkedDescription(
        label=s.label,
        model=s.to_model(),
        terms=RelMark.sort(rels),
    )


def find_marked_terms(sentence_uid: UUID) -> list[Term]:
    """文章にマークされた用語を取得."""
    rels = RelMarkUtil.find_by_source_id(sentence_uid)
    return RelMark.sort(rels)


def remove_marks(
    sentence_uid: UUID,
) -> Label[LSentence2, Sentence]:
    """文章のマークをすべて削除し、文字列をマーク前に戻す.

    markの変更はdelete insertで行うため、mark関係を一部残す
    ことはしない
    """
    rels = RelMarkUtil.find_by_source_id(sentence_uid)
    for rel in rels:
        RelMarkUtil.disconnect(rel.valid_uid)
    s = SentenceUtil.find_by_id(sentence_uid).to_model()
    return SentenceUtil.change(
        sentence_uid,
        value=inject2placeholder(
            s.value,
            [t.value for t in RelMark.sort(rels)],
        ),
    )


def remark_sentence(s_uid: UUID, d: Description) -> ReturnMarkedDescription:
    """Reconnect by delete insert."""
    remove_marks(s_uid)
    SentenceUtil.change(s_uid, value=d.placeheld.value)
    return add_description(d)

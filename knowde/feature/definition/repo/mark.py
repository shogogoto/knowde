"""説明文の依存関係解決."""
from __future__ import annotations

from operator import attrgetter
from typing import TYPE_CHECKING, Self

from neomodel import IntegerProperty
from pydantic import BaseModel, Field

from knowde._feature._shared import RelBase, RelUtil
from knowde._feature._shared.repo.label import Label  # noqa: TCH001
from knowde._feature.sentence import SentenceUtil
from knowde._feature.sentence.domain import Sentence
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.term import TermUtil
from knowde._feature.term.domain import Term
from knowde._feature.term.repo.label import LTerm
from knowde.feature.definition.domain.mark import (
    inject2placeholder,
)
from knowde.feature.definition.repo.errors import UndefinedMarkedTermError

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.feature.definition.domain.description import (
        Description,
    )


class RelMark(RelBase):
    """Mark Relationship with order."""

    order = IntegerProperty()

    @classmethod
    def sort(cls, ls: list[Self]) -> list[Term]:
        """Sort by order."""
        rels = sorted(ls, key=attrgetter("order"))
        return [Term.to_model(rel.end_node()) for rel in rels]


RelMarkUtil = RelUtil(
    t_source=LSentence,
    t_target=LTerm,
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
    label: LSentence
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
    lbs = RelMarkUtil.find_by_source_id(sentence_uid)
    lbs = sorted(lbs, key=attrgetter("order"))
    return [Term.to_model(lb.end_node()) for lb in lbs]


def remove_marks(
    sentence_uid: UUID,
    prefix: str = "",
    suffix: str = "",
) -> Label[LSentence, Sentence]:
    """文章のマークをすべて削除し、文字列をマーク前に戻す.

    markの変更はdelete insertで行うため、mark関係を一部残す
    ことはしない
    """
    tvalues = []
    orders = []
    for rel in RelMarkUtil.find_by_source_id(sentence_uid):
        sent_lb = rel.start_node()
        s = Sentence.to_model(sent_lb)
        term_lb = rel.end_node()
        orders.append(rel.order)
        tvalues.append(term_lb.value)
        RelMarkUtil.disconnect(sent_lb, term_lb)

    s = SentenceUtil.find_by_id(sentence_uid).to_model()
    _sorted = [tvalues[i] for i in orders]
    new = inject2placeholder(s.value, _sorted, prefix, suffix)
    return SentenceUtil.change(sentence_uid, value=new)


def remark_sentence(s_uid: UUID, d: Description) -> ReturnMarkedDescription:
    """Reconnect by delete insert."""
    remove_marks(s_uid)
    SentenceUtil.change(s_uid, value=d.placeheld.value)
    return add_description(d)

"""説明文の依存関係解決."""
from __future__ import annotations

from operator import attrgetter
from typing import TYPE_CHECKING

from neomodel import IntegerProperty

from knowde._feature._shared import RelBase, RelUtil
from knowde._feature.sentence import SentenceUtil
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.term import TermUtil
from knowde._feature.term.domain import Term
from knowde._feature.term.repo.label import LTerm
from knowde.feature.definition.domain.description import (
    Description,
    PlaceHeldDescription,
)
from knowde.feature.definition.repo.errors import UndefinedMarkedTermError

if TYPE_CHECKING:
    from uuid import UUID


class RelMark(RelBase):
    """Mark Relationship with order."""

    order = IntegerProperty()


RelMarkUtil = RelUtil(
    t_source=LSentence,
    t_target=LTerm,
    name="MARK",
    t_rel=RelMark,
)


def mark_sentence(sentence_uid: UUID) -> PlaceHeldDescription:
    """markを解決して永続化."""
    s = SentenceUtil.find_by_id(sentence_uid)
    d = Description(value=s.to_model().value)
    for i, mv in enumerate(d.markvalues):
        t = TermUtil.find_one_or_none(value=mv.value)
        if t is None:
            msg = f"用語'{mv.value}'は見つかりませんでした'"
            raise UndefinedMarkedTermError(msg)
        RelMarkUtil.connect(s.label, t.label, order=i)
    return d.placeheld


def find_marked_terms(sentence_uid: UUID) -> list[Term]:
    """文章にマークされた用語を取得."""
    lbs = RelMarkUtil.find_by_source_id(sentence_uid)
    lbs = sorted(lbs, key=attrgetter("order"))
    return [Term.to_model(lb.end_node()) for lb in lbs]


def remove_marks(sentence_uid: UUID) -> None:
    """文章のマークをすべて削除.

    markの変更はdelete insertで行うため、mark関係を一部残す
    ことはしない
    """
    for lb in RelMarkUtil.find_by_source_id(sentence_uid):
        RelMarkUtil.disconnect(lb.start_node(), lb.end_node())


def remark_sentence(s_uid: UUID, value: str) -> None:
    """Reconnect by delete insert."""
    remove_marks(s_uid)
    SentenceUtil.change(s_uid, value=value)
    mark_sentence(s_uid)

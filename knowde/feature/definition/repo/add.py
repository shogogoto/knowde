"""new create repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import (
    RelationshipManager,
    RelationshipTo,
    ZeroOrMore,
)

from knowde._feature._shared.repo.base import RelBase
from knowde._feature.sentence import s_util
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.sentence.repo.query import SentenceQuery
from knowde._feature.term import term_util
from knowde._feature.term.repo.query import TermQuery
from knowde.feature.definition.domain.domain import Definition

if TYPE_CHECKING:
    from knowde._feature.term.repo.label import LTerm


def relation_to(
    source: LTerm,
) -> RelationshipManager:
    """関係先を紐付ける.

    - StructuredNodeにRelPropertyをつけると他のStructuredNodeと依存して
      パッケージの独立性が侵されるため、
    - neomodelのtypingを補完するために
    StructuredNodeとは切り離して関数化した.
    """
    return RelationshipTo(
        cls_name=LSentence,
        relation_type="DEFINE",  # edge名
        cardinality=ZeroOrMore,
        model=RelBase,  # StructuredRel
    ).build_manager(source, name="")  # nameが何に使われているのか不明


def create_definition(name: str, explain: str) -> Definition:
    """Create new definition."""
    t = TermQuery.find_one_or_none(name)
    s = SentenceQuery.find_one_or_none(explain)
    if t is None:
        t = term_util.create(value=name)
    if s is None:
        s = s_util.create(value=explain)

    mgr = relation_to(t.label)
    rel = mgr.connect(s.label)
    return Definition(
        term=t.to_model(),
        sentence=s.to_model(),
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )

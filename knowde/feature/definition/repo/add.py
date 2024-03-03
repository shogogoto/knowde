"""new create repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import (
    RelationshipManager,
    RelationshipTo,
    ZeroOrMore,
)

from knowde._feature._shared.repo.base import RelBase
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.sentence import s_util
from knowde._feature.sentence.domain import Sentence
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.sentence.repo.query import SentenceQuery
from knowde._feature.term import term_util
from knowde._feature.term.domain import Term
from knowde._feature.term.repo.query import TermQuery
from knowde.feature.definition.domain.domain import Definition
from knowde.feature.definition.repo.errors import AlreadyDefinedError

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.term.repo.label import LTerm


def rel_manager(
    source: LTerm,
) -> RelationshipManager:
    """関係先を紐付ける.

    以下のためにStructuredNodeとは切り離して関数化した.
    - StructuredNodeにRelPropertyをつけると他のStructuredNodeと依存して
      パッケージの独立性が侵される
    - neomodelのtypingを補完する
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

    mgr = rel_manager(t.label)
    d = find_definition(t.to_model().valid_uid)
    if d:
        msg = f"定義済みです: {d.oneline}"
        raise AlreadyDefinedError(msg)

    rel = mgr.connect(s.label).save()
    return Definition(
        term=t.to_model(),
        sentence=s.to_model(),
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )


def find_definition(term_uid: UUID) -> Definition | None:
    """neomodelではrelationを検索できないのでcypherで書く."""
    res = query_cypher(
        """
        MATCH (t:Term)-[rel:DEFINE]->(Sentence)
        WHERE t.uid = $uid
        RETURN rel """,
        params={"uid": term_uid.hex},
    ).results
    if len(res) == 0:
        return None
    rel = res[0][0]
    t = Term.to_model(rel.start_node())
    s = Sentence.to_model(rel.end_node())
    return Definition(
        term=t,
        sentence=s,
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )


# def change_definition(
#     d: Definition,
#     name: str | None = None,
#     explain: str | None = None,
# ) -> None:
#     """定義の変更."""

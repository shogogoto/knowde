"""new create repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import ZeroOrOne

from knowde._feature._shared.repo.base import RelBase
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature.sentence.domain import Sentence
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.term import TermUtil
from knowde._feature.term.repo.label import LTerm
from knowde.feature.definition.domain.description import Description
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
from knowde.feature.definition.repo.errors import (
    AlreadyDefinedError,
    DuplicateDefinedError,
)
from knowde.feature.definition.repo.mark import (
    add_description,
    find_marked_terms,
    remark_sentence,
)

if TYPE_CHECKING:
    from uuid import UUID


RelDefUtil = RelUtil(
    t_source=LTerm,
    t_target=LSentence,
    name="DEFINE",
    t_rel=RelBase,
    cardinality=ZeroOrOne,
)


def add_definition(p: DefinitionParam) -> Definition:
    """Create new definition."""
    name = p.name
    t = TermUtil.find_one_or_none(value=name)
    if t is None:
        t = TermUtil.create(value=name)
    d = find_definition(t.to_model().valid_uid)
    if d:
        msg = f"定義済みです: {d.output}"
        raise AlreadyDefinedError(msg)
    d = add_description(Description(value=p.explain))
    rel = RelDefUtil.connect(t.label, d.label)
    return Definition.from_rel(rel, d.terms)


def find_definition(term_uid: UUID) -> Definition | None:
    """neomodelではrelationを検索できないのでcypherで書く."""
    rels = RelDefUtil.find_by_source_id(term_uid)
    if len(rels) == 0:
        return None
    if len(rels) > 1:
        raise DuplicateDefinedError  # 仮実装
    return Definition.from_rel(rels[0])


def change_definition(
    d: Definition,
    name: str | None = None,
    explain: str | None = None,
) -> Definition:
    """定義の変更."""
    if name is not None:
        TermUtil.change(d.term.valid_uid, value=name)

    if explain is not None:
        dscr = Description(value=explain)
        remark_sentence(d.sentence.valid_uid, dscr).to_model()

    rel = RelDefUtil.find_by_source_id(d.term.valid_uid)[0]
    if any([name, explain]):
        rel.save()
    return Definition.from_rel(rel)


def remove_definition(term_uid: UUID) -> None:
    """定義の削除."""
    query_cypher(
        """
        MATCH (:Term {uid: $uid})-[def:DEFINE]->(s:Sentence)
        OPTIONAL MATCH (s)-[mark:MARK]->(:Term)
        DELETE def, mark
        """,
        params={"uid": term_uid.hex},
    )


def complete_definition(pref_uid: str) -> Definition:
    """前方一致検索."""
    # print(RelDefUtil.find_by_source_id(UUID(pref_uid)))
    rel = RelDefUtil.complete(pref_uid=pref_uid)
    s = Sentence.to_model(rel.end_node())
    terms = find_marked_terms(s.valid_uid)
    return Definition.from_rel(rel, deps=terms)

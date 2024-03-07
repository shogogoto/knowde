"""new create repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.repo.base import RelBase
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature.sentence import s_util
from knowde._feature.sentence.domain import Sentence
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.term import term_util
from knowde._feature.term.domain import Term
from knowde._feature.term.repo.label import LTerm
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
from knowde.feature.definition.repo.errors import AlreadyDefinedError

if TYPE_CHECKING:
    from uuid import UUID


rel_def = RelUtil(
    t_source=LTerm,
    t_target=LSentence,
    name="DEFINE",
    t_rel=RelBase,
)


def add_definition(p: DefinitionParam) -> Definition:
    """Create new definition."""
    name = p.name
    explain = p.explain
    t = term_util.find_one_or_none(value=name)
    s = s_util.find_one_or_none(value=explain)
    if t is None:
        t = term_util.create(value=name)
    if s is None:
        s = s_util.create(value=explain)

    d = find_definition(t.to_model().valid_uid)
    if d:
        msg = f"定義済みです: {d.oneline}"
        raise AlreadyDefinedError(msg)

    rel = rel_def.connect(t.label, s.label)
    return Definition(
        term=t.to_model(),
        sentence=s.to_model(),
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )


def get_rel(term_uid: UUID) -> RelBase | None:
    """Get StructuredRel object."""
    res = query_cypher(
        f"""
        MATCH (t:Term)-[rel:{rel_def.name}]->(Sentence)
        WHERE t.uid = $uid
        RETURN rel """,
        params={"uid": term_uid.hex},
    ).results
    if len(res) == 0:
        return None
    return res[0][0]


def find_definition(term_uid: UUID) -> Definition | None:
    """neomodelではrelationを検索できないのでcypherで書く."""
    rel = get_rel(term_uid)
    if rel is None:
        return None
    t = Term.to_model(rel.start_node())
    s = Sentence.to_model(rel.end_node())
    return Definition(
        term=t,
        sentence=s,
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )


def change_definition(
    d: Definition,
    name: str | None = None,
    explain: str | None = None,
) -> Definition:
    """定義の変更."""
    rel = get_rel(d.term.valid_uid)

    t = term_util.change(d.term.valid_uid, value=name).to_model()
    s = s_util.change(d.sentence.valid_uid, value=explain).to_model()

    if any([name, explain]):
        rel.save()

    return Definition(
        term=t,
        sentence=s,
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )

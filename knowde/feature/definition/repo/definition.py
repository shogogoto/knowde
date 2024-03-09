"""new create repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.repo.base import RelBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature.sentence import SentenceUtil
from knowde._feature.sentence.domain import Sentence
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.term import TermUtil
from knowde._feature.term.domain import Term
from knowde._feature.term.repo.label import LTerm
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
from knowde.feature.definition.repo.errors import AlreadyDefinedError

if TYPE_CHECKING:
    from uuid import UUID


RelDef = RelUtil(
    t_source=LTerm,
    t_target=LSentence,
    name="DEFINE",
    t_rel=RelBase,
)


def add_definition(p: DefinitionParam) -> Definition:
    """Create new definition."""
    name = p.name
    explain = p.explain
    t = TermUtil.find_one_or_none(value=name)
    s = SentenceUtil.find_one_or_none(value=explain)
    if t is None:
        t = TermUtil.create(value=name)
    if s is None:
        s = SentenceUtil.create(value=explain)

    d = find_definition(t.to_model().valid_uid)
    if d:
        msg = f"定義済みです: {d.oneline}"
        raise AlreadyDefinedError(msg)

    rel = RelDef.connect(t.label, s.label)
    return Definition(
        term=t.to_model(),
        sentence=s.to_model(),
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )


def find_definition(term_uid: UUID) -> Definition | None:
    """neomodelではrelationを検索できないのでcypherで書く."""
    rels = RelDef.find_by_source_id(term_uid)
    if len(rels) == 0:
        return None
    rel = rels[0]
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
    rel = RelDef.find_by_source_id(d.term.valid_uid)[0]

    t = TermUtil.change(d.term.valid_uid, value=name).to_model()
    s = SentenceUtil.change(d.sentence.valid_uid, value=explain).to_model()

    if any([name, explain]):
        rel.save()

    return Definition(
        term=t,
        sentence=s,
        uid=rel.uid,
        created=rel.created,
        updated=rel.updated,
    )

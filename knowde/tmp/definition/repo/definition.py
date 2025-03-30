"""new create repository."""

from __future__ import annotations

from operator import itemgetter
from uuid import UUID

from neomodel import ZeroOrOne

from knowde.primitive.__core__.label_repo.base import RelBase
from knowde.primitive.__core__.label_repo.query import QueryResult, query_cypher
from knowde.primitive.__core__.label_repo.rel import RelUtil
from knowde.tmp.definition.domain.description import Description
from knowde.tmp.definition.domain.domain import Definition
from knowde.tmp.definition.domain.statistics import (
    DepStatistics,
    StatsDefinition,
    StatsDefinitions,
)
from knowde.tmp.definition.repo.errors import (
    AlreadyDefinedError,
)
from knowde.tmp.definition.repo.label import REL_DEF_LABEL
from knowde.tmp.definition.repo.mark import (
    RelMark,
    add_description,
    find_marked_terms,
    remark_sentence,
)
from knowde.tmp.definition.repo.statistics import statistics_query
from knowde.tmp.definition.sentence import LSentence2
from knowde.tmp.definition.sentence.domain import Sentence
from knowde.tmp.definition.term import LTerm2, TermUtil

RelDefUtil = RelUtil(
    t_source=LTerm2,
    t_target=LSentence2,
    name=REL_DEF_LABEL,
    t_rel=RelBase,
    cardinality=ZeroOrOne,
)


# 引数がDTOなのはこの関数をinterfaceにぶち込んでるから
def add_definition(name: str, explain: str) -> Definition:
    """Create new definition."""
    t = TermUtil.find_one_or_none(value=name)
    if t is None:
        t = TermUtil.create(value=name)

    rels = RelDefUtil.find_by_source_id(t.to_model().valid_uid)
    if len(rels) >= 1:
        msg = "定義済みです"
        raise AlreadyDefinedError(msg)
    d = add_description(Description(value=explain))
    rel = RelDefUtil.connect(t.label, d.label)
    return Definition.from_rel(rel, d.terms)


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


def remove_definition(def_uid: UUID) -> None:
    """定義の削除."""
    query_cypher(
        """
        MATCH (:Term)-[def:DEFINE {uid: $uid}]->(s:Sentence)
        OPTIONAL MATCH (s)-[mark:MARK]->(:Term)
        DELETE def, mark
        """,
        params={"uid": def_uid.hex},
    )


def complete_definition(pref_uid: str) -> Definition:
    """前方一致検索."""
    rel = RelDefUtil.complete(pref_rel_uid=pref_uid)
    s = Sentence.to_model(rel.end_node())
    terms = find_marked_terms(s.valid_uid)
    return Definition.from_rel(rel, deps=terms)


def q_stats_def() -> str:
    """Cypher path pattern."""
    return f"""
        OPTIONAL MATCH (s)-[m:MARK]->(:Term)
        {statistics_query("s", ["def", "m"])}
        RETURN
            def,
            collect(m) as marks,
            n_src,
            n_dest,
            max_leaf_dist,
            max_root_dist
        """


def build_statsdefs(res: QueryResult) -> StatsDefinitions:
    """Build from query result."""
    terms = res.get("marks", RelMark.sort, row_convert=itemgetter(0))
    drels, n_srcs, n_dests, max_leaf_dists, max_root_dists = res.tuple(
        "def",
        "n_src",
        "n_dest",
        "max_leaf_dist",
        "max_root_dist",
    )
    retvals = []
    for t, rel, n_src, n_dest, mld, mrd in zip(
        terms,
        drels,
        n_srcs,
        n_dests,
        max_leaf_dists,
        max_root_dists,
        strict=True,
    ):
        sd = StatsDefinition(
            definition=Definition.from_rel(rel, t),
            statistics=DepStatistics(
                n_src=n_src,
                n_dest=n_dest,
                max_leaf_dist=mld,
                max_root_dist=mrd,
            ),
        )
        retvals.append(sd)

    return StatsDefinitions(values=retvals)


def list_definitions() -> StatsDefinitions:
    """とりあえず一覧を返す.

    本当は依存関係の統計値も返したいが、開発が進んでから再検討しよう
    """
    res = query_cypher(
        f"""
        MATCH (:Term)-[def:DEFINE]->(s:Sentence)
        {q_stats_def()}
        """,
    )
    return build_statsdefs(res)

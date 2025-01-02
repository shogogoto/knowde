"""repo."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from knowde.primitive.__core__.label_repo.query import query_cypher
from knowde.tmp.definition.domain.statistics import DepStatistics
from knowde.tmp.definition.repo.label import REL_DEF_LABEL
from knowde.tmp.definition.repo.mark import RelMarkUtil

if TYPE_CHECKING:
    from uuid import UUID


def statistics_query(
    sentence_var: str,
    with_vars: Optional[list[str]] = None,
) -> str:
    """依存統計."""
    with_s = "" if with_vars is None else ",".join(with_vars) + ","
    mn = RelMarkUtil.name
    dn = REL_DEF_LABEL
    s = sentence_var
    return f"""
        // Sentenceの数だけ数えればよい
        OPTIONAL MATCH src = ({s})-[:{mn}|{dn}]->+(s_src:Sentence)
        OPTIONAL MATCH dest = ({s})<-[:{mn}|{dn}]-+(s_dest:Sentence)
        OPTIONAL MATCH leaf = ({s})-[:{mn}|{dn}]->+(lf:Sentence)
            WHERE NOT (lf)<-[:{mn}]-(:Term)
        OPTIONAL MATCH root = ({s})<-[:{mn}|{dn}]-+(rt:Sentence)
            WHERE NOT (rt)<-[:{mn}]-(:Term)
        WITH
            {with_s}
            count(DISTINCT s_src) as n_src,
            count(DISTINCT s_dest) as n_dest,
            // s1<-[:def]<-t1<-[:mark]<-s2 というように2つのrelがあるので割る2
            max(coalesce(length(leaf), 0)) / 2 as max_leaf_dist,
            max(coalesce(length(root), 0)) / 2 as max_root_dist
    """


def find_statistics(def_uid: UUID) -> DepStatistics:
    """定義の依存統計を取得."""
    dn = REL_DEF_LABEL
    res = query_cypher(
        f"""
        MATCH (:Term)-[def:{dn} {{uid: $uid}}]->(s:Sentence)
        {statistics_query("s")}
        RETURN
            n_src,
            n_dest,
            max_leaf_dist,
            max_root_dist
        """,
        params={"uid": def_uid.hex},
    )

    return DepStatistics(
        n_src=res.get("n_src")[0],
        n_dest=res.get("n_dest")[0],
        max_leaf_dist=res.get("max_leaf_dist")[0],
        max_root_dist=res.get("max_root_dist")[0],
    )

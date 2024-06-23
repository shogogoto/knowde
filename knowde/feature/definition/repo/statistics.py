"""repo."""
from uuid import UUID

from knowde._feature._shared.repo.query import query_cypher
from knowde.feature.definition.domain.statistics import DepStatistics
from knowde.feature.definition.repo.definition import RelDefUtil
from knowde.feature.definition.repo.mark import RelMarkUtil


def find_statistics(def_uid: UUID) -> DepStatistics:
    """定義の依存統計を取得."""
    mn = RelMarkUtil.name
    dn = RelDefUtil.name
    res = query_cypher(
        f"""
        MATCH (t:Term)-[def:{dn} {{uid: $uid}}]->(s:Sentence)
        // Sentenceの数だけ数えればよい
        OPTIONAL MATCH src = (t)<-[:{mn}|{dn}]-+(s_src:Sentence)
        OPTIONAL MATCH dest = (s)-[:{mn}|{dn}]->+(s_dest:Sentence)
        OPTIONAL MATCH leaf = (s)<-[:{mn}|{dn}]-+(lf:Sentence)
            WHERE NOT (lf)<-[:{mn}]-(:Term)
        OPTIONAL MATCH root = (s)-[:{mn}|{dn}]->+(rt:Sentence)
            WHERE NOT (rt)<-[:{mn}]-(:Term)
        RETURN
            leaf,
            root,
            count(DISTINCT s_src) as n_src,
            count(DISTINCT s_dest) as n_dest,
            // s1<-[:def]<-t1<-[:mark]<-s2 というように2つのrelがあるので割る2
            length(leaf) / 2 as max_leaf_dist,
            length(root) / 2 as max_root_dist
        """,
        params={"uid": def_uid.hex},
    )

    # print("################################## res")
    # print("################################## res")
    # for row in res.get("leaf"):
    #     print(row)
    # print("################################## res")

    # for row in res.get("root"):
    #     print(row)
    return DepStatistics(
        n_src=res.get("n_src")[0],
        n_dest=res.get("n_dest")[0],
        max_leaf_dist=res.get("max_leaf_dist")[0],
        max_root_dist=res.get("max_root_dist")[0],
    )

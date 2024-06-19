"""repo."""
from uuid import UUID

from knowde.feature.definition.domain.statistics import DepStatistics


def find_statistics(_def_uid: UUID) -> DepStatistics:
    """定義の依存統計を取得."""
    return DepStatistics(
        n_deps=0,
        n_roots=0,
        max_root_dist=0,
        max_leaf_dist=0,
    )
    # mn = RelMarkUtil.name
    # dn = RelDefUtil.name
    # res = query_cypher(
    #     f"""
    #     MATCH (t1:Term)-[def:{dn} {{uid: $uid}}]->(s:Sentence)
    #     OPTIONAL MATCH p = (s)-[:{mn}|{dn}]->*(:Term)-[:{dn}]->(:Sentence)
    #     RETURN p, def
    #     """,
    #     params={"uid": def_uid.hex},
    # )

"""repo of deduction stats."""
from uuid import UUID

from knowde._feature._shared.repo.query import query_cypher
from knowde.feature.proposition.domain import DeductionStatistics
from knowde.feature.proposition.repo.label import (
    REL_CONCLUSION_LABEL,
    REL_PREMISE_LABEL,
)


def find_deductstats(uid: UUID) -> DeductionStatistics:
    """演繹の依存統計."""
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    rel = f"-[:{pl}|{cl}]-"
    res = query_cypher(
        f"""
        MATCH (d:Deduction {{uid: $uid}})
        OPTIONAL MATCH src = (s_:Proposition){rel}>+(d)
        OPTIONAL MATCH dest = (d){rel}>+(d_:Proposition)
        OPTIONAL MATCH axiom = (a_){rel}>+(d)
            WHERE NOT (a_)<{rel}()
        OPTIONAL MATCH leaf = (d){rel}>+(l_:Proposition)
            WHERE NOT (l_){rel}>()
        WITH
            count(DISTINCT s_) as n_src,
            count(DISTINCT d_) as n_dest,
            count(DISTINCT a_) as n_axiom,
            count(DISTINCT l_) as n_leaf,
            (max(length(axiom)) + 1) / 2 as max_axiom_dist,
            (max(length(leaf)) + 1) / 2 as max_leaf_dist
        RETURN
            n_src,
            n_dest,
            n_axiom,
            n_leaf,
            max_axiom_dist,
            max_leaf_dist
        """,
        params={"uid": uid.hex},
    )
    return DeductionStatistics(
        n_src=res.get("n_src")[0],
        n_dest=res.get("n_dest")[0],
        n_axiom=res.get("n_axiom")[0],
        n_leaf=res.get("n_leaf")[0],
        max_axiom_dist=res.get("max_axiom_dist")[0],
        max_leaf_dist=res.get("max_leaf_dist")[0],
    )

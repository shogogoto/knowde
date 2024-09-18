"""repo of deduction stats."""
from __future__ import annotations

from typing import TYPE_CHECKING, Final, Optional

from knowde.complex.deduction.domain import DeductionStatistics
from knowde.complex.deduction.repo.label import (
    REL_CONCLUSION_LABEL,
    REL_PREMISE_LABEL,
)
from knowde.core.label_repo.query import query_cypher

if TYPE_CHECKING:
    from uuid import UUID


def q_deduction_stats(
    deduction_var: str,
    with_vars: Optional[list[str]] = None,
) -> str:
    """演繹統計用query."""
    d = deduction_var
    with_s = "" if with_vars is None else ",".join(with_vars) + ","
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    rel = f"-[:{pl}|{cl}]-"
    return f"""
        OPTIONAL MATCH src = (s_:Proposition){rel}>+({d})
        OPTIONAL MATCH dest = ({d}){rel}>+(d_:Proposition)
        OPTIONAL MATCH axiom = (a_){rel}>+({d})
            WHERE NOT (a_)<{rel}()
        OPTIONAL MATCH leaf = ({d}){rel}>+(l_:Proposition)
            WHERE NOT (l_){rel}>()
        WITH
            {with_s}
            count(DISTINCT s_) as n_src,
            count(DISTINCT d_) as n_dest,
            count(DISTINCT a_) as n_axiom,
            count(DISTINCT l_) as n_leaf,
            (max(length(axiom)) + 1) / 2 as max_axiom_dist,
            (max(length(leaf)) + 1) / 2 as max_leaf_dist
    """


DEDUCTION_STATS_VARS: Final = [
    "n_src",
    "n_dest",
    "n_axiom",
    "n_leaf",
    "max_axiom_dist",
    "max_leaf_dist",
]


def find_deductstats(uid: UUID) -> DeductionStatistics:
    """演繹の依存統計."""
    res = query_cypher(
        f"""
        MATCH (d:Deduction {{uid: $uid}})
        {q_deduction_stats("d")}
        RETURN {",".join(DEDUCTION_STATS_VARS)}
        """,
        params={"uid": uid.hex},
    )
    return DeductionStatistics.create(res.item(0, *DEDUCTION_STATS_VARS))

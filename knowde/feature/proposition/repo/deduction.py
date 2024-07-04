"""論証."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from knowde._feature._shared.domain import jst_now
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature._shared.repo.util import NeomodelUtil
from knowde._feature.proposition.domain import Proposition
from knowde.feature.proposition.domain import (
    Deduction,
    DeductionStatistics,
    StatsDeduction,
    StatsDeductions,
)
from knowde.feature.proposition.repo.label import (
    REL_CONCLUSION_LABEL,
    REL_PREMISE_LABEL,
    LDeduction,
    RelPremise,
)
from knowde.feature.proposition.repo.statistics import (
    DEDUCTION_STATS_VARS,
    q_deduction_stats,
)

if TYPE_CHECKING:
    from uuid import UUID


def deduct(
    txt: str,
    premise_ids: list[UUID],
    conclusion_id: UUID,
    valid: bool = True,  # noqa: FBT001 FBT002
) -> Deduction:
    """演繹を永続化."""
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    # neomodelを活かせていない気がする
    res = query_cypher(
        f"""
        MATCH (c:Proposition {{uid: $cid}})
        CREATE (d:Deduction {{
            text: $txt,
            valid: $valid,
            created: $now,
            updated: $now,
            uid: $uid
        }})-[:{cl}]->(c)
        WITH c, d
        UNWIND range(0, size($pids) - 1) as i
        WITH c, d, i, $pids[i] as pid
        MATCH (pre:Proposition {{uid: pid}})
        CREATE (pre)-[rel:{pl} {{order: i}}]->(d)
        RETURN c, d, pre
        """,
        params={
            "txt": txt,
            "valid": valid,
            "pids": [pid.hex for pid in premise_ids],
            "cid": conclusion_id.hex,
            "now": jst_now().timestamp(),
            "uid": uuid4().hex,
        },
    )
    d = res.get("d")[0]
    return Deduction(
        text=txt,
        premises=res.get("pre", convert=Proposition.to_model),
        conclusion=res.get("c", convert=Proposition.to_model)[0],
        valid=valid,
        uid=d.uid,
        created=d.created,
        updated=d.updated,
    )


def remove_deduction(uid: UUID) -> None:
    """演繹の削除."""
    NeomodelUtil(t=LDeduction).delete(uid)


def list_deductions() -> StatsDeductions:
    """演繹一覧."""
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    res = query_cypher(
        f"""
        MATCH (d:Deduction)-[:{cl}]->(c:Proposition)
        OPTIONAL MATCH (d)<-[rel:{pl}]-(pre:Proposition)
        {q_deduction_stats("d", ["d", "c", "rel"])}
        RETURN
            {",".join(DEDUCTION_STATS_VARS)},
            d,
            c,
            rel
        """,
    )
    d = {}
    cnt = 0
    for lb, c, rel in zip(
        res.get("d"),
        res.get("c", convert=Proposition.to_model),
        res.get("rel"),  # , convert=Proposition.to_models),
        strict=True,
    ):
        if lb.uid not in d:
            d[lb.uid] = {
                "lb": lb,
                "c": c,
                "stats": DeductionStatistics.create(
                    res.item(cnt, *DEDUCTION_STATS_VARS),
                ),
            }
        if "rels" in d[lb.uid]:
            d[lb.uid]["rels"].append(rel)
        else:
            d[lb.uid]["rels"] = [rel]
        cnt += 1

    retvals = []
    for uid in d:
        lb = d[uid]["lb"]
        c = d[uid]["c"]
        rels = d[uid]["rels"]
        deduction = Deduction(
            text=lb.text,
            premises=RelPremise.sort(rels),
            conclusion=c,
            valid=lb.valid,
            uid=lb.uid,
            created=lb.created,
            updated=lb.updated,
        )
        retvals.append(
            StatsDeduction(deduction=deduction, stats=d[uid]["stats"]),
        )

    return StatsDeductions(values=retvals)

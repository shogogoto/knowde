"""論証."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from knowde._feature._shared.domain import jst_now
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature._shared.repo.util import NeomodelUtil
from knowde.feature.proposition.domain import Deduction, Proposition
from knowde.feature.proposition.repo.label import (
    REL_CONCLUSION_LABEL,
    REL_PREMISE_LABEL,
    LDeduction,
    RelPremise,
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
        UNWIND $pids as pid
        MATCH (c:Proposition {{uid: $cid}})
        MATCH (pre:Proposition WHERE pre.uid = pid)
        CREATE (d:Deduction {{
            text: $txt,
            valid: $valid,
            created: $now,
            updated: $now,
            uid: $uid
        }})-[:{cl}]->(c)
        WITH c, d, pre,
            collect(pre) as pres
        UNWIND range(0, size(pres) - 1) as i
        WITH c, d, pre, pres[i] as i_pre, i
        CREATE (d)-[rel:{pl} {{order: i}}]->(i_pre)
        RETURN c, d, i_pre
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
        premises=res.get("i_pre", convert=Proposition.to_model),
        conclusion=res.get("c", convert=Proposition.to_model)[0],
        valid=valid,
        uid=d.uid,
        created=d.created,
        updated=d.updated,
    )


def remove_deduction(uid: UUID) -> None:
    """演繹の削除."""
    NeomodelUtil(t=LDeduction).delete(uid)


def list_deductions() -> list[Deduction]:
    """演繹一覧."""
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    res = query_cypher(
        f"""
        MATCH (d:Deduction)-[:{cl}]->(c:Proposition)
        OPTIONAL MATCH (d)-[rel:{pl}]->(pre:Proposition)
        RETURN
            d,
            c,
            rel
        """,
    )
    d = {}
    for lb, c, rel in zip(
        res.get("d"),
        res.get("c", convert=Proposition.to_model),
        res.get("rel"),  # , convert=Proposition.to_models),
        strict=True,
    ):
        if lb.uid not in d:
            d[lb.uid] = {"lb": lb, "c": c}
        if "rels" in d[lb.uid]:
            d[lb.uid]["rels"].append(rel)
        else:
            d[lb.uid]["rels"] = [rel]

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
        retvals.append(deduction)

    return retvals

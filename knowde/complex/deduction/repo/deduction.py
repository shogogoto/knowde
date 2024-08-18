"""論証."""
from __future__ import annotations

import collections
from uuid import UUID, uuid4

from knowde.complex.deduction.domain import (
    Deduction,
    DeductionStatistics,
    StatsDeduction,
    StatsDeductions,
)
from knowde.complex.deduction.repo.errors import (
    CyclicDependencyError,
    NoPremiseError,
    PremiseDuplicationError,
)
from knowde.complex.deduction.repo.label import (
    REL_CONCLUSION_LABEL,
    REL_PREMISE_LABEL,
    DeductionMapper,
    LDeduction,
    RelPremise,
)
from knowde.complex.deduction.repo.statistics import (
    DEDUCTION_STATS_VARS,
    q_deduction_stats,
)
from knowde.core import jst_now
from knowde.core.errors.domain import NeomodelNotFoundError
from knowde.core.repo.query import query_cypher
from knowde.core.repo.util import LabelUtil
from knowde.primitive.proposition.domain import Proposition


def check_premises_and_conclusion(premise_ids: list[UUID], conclusion_id: UUID) -> None:
    """前提と結論の妥当性チェック."""
    if conclusion_id in premise_ids:
        msg = f"結論({conclusion_id})が前提に含まれています"
        raise CyclicDependencyError(msg)

    if len(premise_ids) == 0:
        msg = "前提がありません"
        raise NoPremiseError(msg)

    cnt = collections.Counter(premise_ids)
    for uid, c in cnt.items():
        if c > 1:
            msg = f"前提{uid}が重複しています"
            raise PremiseDuplicationError(msg)


def deduct(
    txt: str,
    premise_ids: list[UUID],
    conclusion_id: UUID,
    valid: bool = True,  # noqa: FBT001 FBT002
) -> Deduction:
    """演繹を永続化."""
    check_premises_and_conclusion(premise_ids, conclusion_id)
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
        RETURN c, d, rel
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
        text=d.text,
        premises=RelPremise.sort(res.get("rel")),
        conclusion=res.get("c", convert=Proposition.to_model)[0],
        valid=d.valid,
        uid=d.uid,
        created=d.created,
        updated=d.updated,
    )


def find_deduction_by_uid(uid: UUID) -> Deduction:
    """前提や結論を含めた演繹を探す."""
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    res = query_cypher(
        f"""
        MATCH (d:Deduction {{uid: $uid}})-[:{cl}]->(c:Proposition),
            (d)<-[rel:{pl}]-(pre:Proposition)
        RETURN d, c, rel
        """,
        params={"uid": uid.hex},
    )
    if len(res.results) == 0:
        msg = f"{uid}は見つかりませんでした"
        raise NeomodelNotFoundError(msg)
    lb = res.get("d")[0]
    return Deduction(
        text=lb.text,
        premises=RelPremise.sort(res.get("rel")),
        conclusion=res.get("c", convert=Proposition.to_model)[0],
        valid=lb.valid,
        uid=lb.uid,
        created=lb.created,
        updated=lb.updated,
    )


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
        res.get("rel"),
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


MDeductionUtil = LabelUtil(label=LDeduction, model=DeductionMapper)


def remove_deduction(uid: UUID) -> None:
    """演繹の削除."""
    MDeductionUtil.delete(uid)


def complete_deduction_mapper(pref_uid: str) -> DeductionMapper:
    """補完."""
    return MDeductionUtil.complete(pref_uid).to_model()


def _check_premise_replace(
    d_id: UUID,
    premise_ids: list[UUID],
) -> None:
    """cyclicチェック."""
    d = find_deduction_by_uid(d_id)
    conclusion_id = d.conclusion.valid_uid
    check_premises_and_conclusion(premise_ids, conclusion_id)


def replace_premises(uid: UUID, premise_uids: list[UUID]) -> Deduction:
    """演繹の依存命題を置換."""
    _check_premise_replace(uid, premise_uids)
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    res = query_cypher(
        f"""
        MATCH (d:Deduction {{uid: $did}})<-[rel:{pl}]-(:Proposition),
            (d)-[:{cl}]->(c:Proposition)
        DELETE rel
        WITH DISTINCT d, c
        UNWIND range(0, size($pids) - 1) as i
        WITH d, c, i, $pids[i] as pid
        MATCH (pre:Proposition {{uid: pid}})
        CREATE (pre)-[rel:{pl} {{order: i}}]->(d)
        RETURN c, d, rel
        """,
        params={
            "did": uid.hex,
            "pids": [pid.hex for pid in premise_uids],
        },
    )
    if len(res.results) == 0:
        msg = f"{uid}は見つかりませんでした"
        raise NeomodelNotFoundError(msg)
    d = res.get("d")[0]
    return Deduction(
        text=d.text,
        premises=RelPremise.sort(res.get("rel")),
        conclusion=res.get("c", convert=Proposition.to_model)[0],
        valid=d.valid,
        uid=d.uid,
        created=d.created,
        updated=d.updated,
    )


def _check_conclusion_replace(d_id: UUID, conclusion_id: UUID) -> None:
    """cyclicチェック."""
    d = find_deduction_by_uid(d_id)
    premise_ids = [p.valid_uid for p in d.premises]
    check_premises_and_conclusion(premise_ids, conclusion_id)


def replace_conclusion(uid: UUID, conclusion_uid: UUID) -> Deduction:
    """演繹の結論を置換."""
    _check_conclusion_replace(uid, conclusion_uid)
    cl = REL_CONCLUSION_LABEL
    pl = REL_PREMISE_LABEL
    res = query_cypher(
        f"""
        MATCH (d:Deduction {{uid: $did}}),
            (d)-[old_rel:{cl}]->(:Proposition)
        DELETE old_rel
        WITH  d
        MATCH (c:Proposition {{uid: $cid}})
        CREATE (d)-[:{cl}]->(c)
        WITH d, c
        MATCH (:Proposition)-[rel:{pl}]->(d)
        RETURN rel, d, c
        """,
        params={
            "did": uid.hex,
            "cid": conclusion_uid.hex,
        },
    )
    if len(res.results) == 0:
        msg = f"{uid}は見つかりませんでした"
        raise NeomodelNotFoundError(msg)
    d = res.get("d")[0]
    return Deduction(
        text=d.text,
        premises=RelPremise.sort(res.get("rel")),
        conclusion=res.get("c", convert=Proposition.to_model)[0],
        valid=d.valid,
        uid=d.uid,
        created=d.created,
        updated=d.updated,
    )

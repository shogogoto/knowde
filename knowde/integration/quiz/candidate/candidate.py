"""誤答肢.

>>誤答肢(distractor)は、受験者たちの一般的な誤解やよくある間違いに基づくもので、
>>正解の選択肢と混同しやすいなど合理的に誤解され得る内容でなければなりません.

正解は簡単に決まる
誤答を上手く選ぶことがクイズ機能の主
DBから直接探すのがいい sysnetを復元するのは非効率

誤答肢を見て、これ何だろう、と思ったらクイズチェーンでそこからクイズを
作っていける
"""

from typing import Annotated
from uuid import UUID

from neomodel import adb
from pydantic import Field, TypeAdapter

from knowde.feature.knowde.repo.clause import OrderBy
from knowde.feature.knowde.repo.cypher import q_stats
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.shared.types import UUIDy, to_uuid


# list_candidates_by_radiusで呼べるからこれを直接呼ぶことはなさそう
async def _list_candidates_in_resource(
    target_sent_id: UUIDy,
    must_has_term: bool = False,  # noqa: FBT001, FBT002
):
    """リソース内全ての単文を選択肢候補として列挙."""
    q_term = "<-[:DEF]-(:Term)" if must_has_term else ""
    q = f"""
        MATCH (sent:Sentence {{uid: $sent_uid}})
        OPTIONAL MATCH (s:Sentence {{resource_uid: sent.resource_uid}})
            {q_term}
        WHERE s.uid <> sent.uid
        RETURN DISTINCT s.uid
    """
    uid = to_uuid(target_sent_id).hex
    rows, _ = await adb.cypher_query(q, params={"sent_uid": uid})
    return [row[0] for row in rows]


type Radius = Annotated[int, Field(gt=0, title="探索半径")]
r_adapter = TypeAdapter(Radius)


async def list_candidates_by_radius(
    target_sent_id: UUIDy,
    radius: Radius | None = None,  # Noneの時にリソース内全てを返す
    must_has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """距離指定で選択肢候補を列挙."""
    if radius is None:
        return await _list_candidates_in_resource(
            target_sent_id,
            must_has_term=must_has_term,
        )

    radius = r_adapter.validate_python(radius)
    q_term = "<-[:DEF]-(:Term)" if must_has_term else ""
    q = f"""
        MATCH (sent:Sentence {{uid: $sent_uid}})
        // dist=1.. にすることで sent_uidを含めない
        OPTIONAL MATCH p = (sent)-[]-{{1, {radius}}}(e:Sentence)
            {q_term}
        RETURN DISTINCT e.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"sent_uid": to_uuid(target_sent_id).hex},
    )
    return [row[0] for row in rows]


# 重要な単文を選択肢に混ぜて単純接触効果による学習効果を狙う
async def list_top_scoring_candidates(
    target_sent_id: UUIDy,
    n_candidate: int,
    must_has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """スコアの上位から候補を出す."""
    q_term = "<-[:DEF]-(:Term)" if must_has_term else ""
    order_by = OrderBy()
    q = f"""
        MATCH (tgt:Sentence {{uid: $sent_uid}})
        MATCH (sent: Sentence {{resource_uid: tgt.resource_uid}})
            {q_term}
        WHERE sent.uid <> tgt.uid // 対象を除く
        {q_stats("sent", order_by)}
        {(order_by.phrase())}
        LIMIT $n_candidate
        RETURN DISTINCT sent.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "sent_uid": to_uuid(target_sent_id).hex,
            "n_candidate": n_candidate,
        },
    )
    return [row[0] for row in rows]


async def list_candidates(
    target_sent_id: UUIDy,
    t: CandidateType,
    must_has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """タイプに従って候補を返す."""
    if t.is_radius_type():
        return await list_candidates_by_radius(
            target_sent_id,
            must_has_term=must_has_term,
            **t.config,
        )

    return await list_top_scoring_candidates(
        target_sent_id,
        must_has_term=must_has_term,
        **t.config,
    )

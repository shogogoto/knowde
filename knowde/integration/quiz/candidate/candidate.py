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
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import UUIDy, to_uuid


# list_candidates_by_radiusで呼べるからこれを直接呼ぶことはなさそう
async def _list_candidates_in_resource(
    target_sent_ids: list[UUIDy],
    must_has_term: bool = False,  # noqa: FBT001, FBT002
):
    """リソース内全ての単文を選択肢候補として列挙."""
    q_term = "<-[:DEF]-(:Term)" if must_has_term else ""
    q = f"""
        UNWIND $sent_uids AS sent_uid
        MATCH (sent:Sentence {{uid: sent_uid}})
        OPTIONAL MATCH (s:Sentence {{resource_uid: sent.resource_uid}})
            {q_term}
        WHERE s.uid <> sent.uid
        RETURN DISTINCT s.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "sent_uids": [to_uuid(uid).hex for uid in target_sent_ids],
        },
    )
    return [row[0] for row in rows]


type Radius = Annotated[int, Field(gt=0, title="探索半径")]
r_adapter = TypeAdapter(Radius)


async def list_candidates_by_radius(
    target_sent_ids: list[UUIDy],
    radius: Radius | None = None,  # Noneの時にリソース内全てを返す
    must_has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """距離指定で選択肢候補を列挙."""
    if radius is None:
        return await _list_candidates_in_resource(
            target_sent_ids,
            must_has_term=must_has_term,
        )

    radius = r_adapter.validate_python(radius)
    q_term = "<-[:DEF]-(:Term)" if must_has_term else ""
    q = f"""
        UNWIND $sent_uids AS sent_uid
        MATCH (sent:Sentence {{uid: sent_uid}})
        // dist=1.. にすることで sent_uidを含めない
        OPTIONAL MATCH p = (sent)-[]-{{1, {radius}}}(e:Sentence)
            {q_term}
        RETURN DISTINCT e.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "sent_uids": [to_uuid(uid).hex for uid in target_sent_ids],
        },
    )
    return [row[0] for row in rows]


# 重要な単文を選択肢に混ぜて単純接触効果による学習効果を狙う
async def list_top_scoring_candidates(
    resource_uid: UUIDy,
    n_candidate: int,
    must_has_term: bool = False,  # noqa: FBT001, FBT002
    except_sent_uids: list[UUIDy] | None = None,
    has_quiz: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """スコアの上位から候補を出す."""
    if except_sent_uids is None:
        except_sent_uids = []
    q_term = "<-[:DEF]-(:Term)" if must_has_term else ""
    q_has = "<-[:QUIZ_TARGET]-(:Quiz)" if has_quiz else ""
    order_by = OrderBy()
    q = f"""
        MATCH (sent: Sentence {{resource_uid: $resource_uid}})
            {q_term}
            {q_has}
        WHERE NOT sent.uid IN $except_sent_uids
        {q_stats("sent", order_by)}
        {(order_by.phrase())}
        LIMIT $n_candidate
        RETURN DISTINCT sent.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "resource_uid": to_uuid(resource_uid).hex,
            # 対象単文を除いて指定数を返してほしい
            "n_candidate": n_candidate + 1,
            "except_sent_uids": [to_uuid(uid).hex for uid in except_sent_uids],
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
            [target_sent_id],
            must_has_term=must_has_term,
            **t.config,
        )

    s = LSentence.nodes.get(uid=to_uuid(target_sent_id).hex)
    return await list_top_scoring_candidates(
        s.resource_uid,
        must_has_term=must_has_term,
        except_sent_uids=[target_sent_id],
        **t.config,
    )


async def list_distractors():
    """誤答肢の取得."""

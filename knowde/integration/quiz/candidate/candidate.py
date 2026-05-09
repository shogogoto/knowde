"""クイズの選択肢候補."""

from typing import Annotated
from uuid import UUID

from neomodel import adb
from pydantic import Field, TypeAdapter

from knowde.feature.knowde.repo import search_knowde_ids
from knowde.feature.knowde.repo.clause import OrderBy
from knowde.shared.cypher import Paging
from knowde.shared.types import UUIDy, to_uuid


# sent2resource_uid { sent_uid: resource_uid }
async def fetch_sent2resource_id(sent_ids: list[UUIDy]):
    """単文IDをそのリソースのIDへ変換."""
    q = """
        UNWIND $sent_uids AS sent_uid
        MATCH (sent:Sentence {uid: sent_uid})
        RETURN DISTINCT sent.resource_uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"sent_uids": [to_uuid(uid).hex for uid in sent_ids]},
    )
    return [row[0] for row in rows]


ENOUGH_PAGING = Paging(size=999999)  # 十分な大きさ


async def list_candidates_in_resource(
    target_sent_ids: list[UUIDy],
    only_with_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """リソース内全ての単文uidを選択肢候補として列挙."""
    rs_uids = await fetch_sent2resource_id(target_sent_ids)
    uids = await search_knowde_ids(
        "",
        paging=ENOUGH_PAGING,
        order_by=None,  # 無駄な並び替え省く
        filter_resource_uids=rs_uids,
        only_with_term=only_with_term,
    )
    exclude = set(target_sent_ids)
    return [u for u in uids if u not in exclude]


type Radius = Annotated[int, Field(gt=0, title="探索半径")]
r_adapter = TypeAdapter(Radius)


async def list_candidates_by_radius(
    target_sent_ids: list[UUIDy],
    radius: int,
    only_with_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """距離指定で選択肢候補を列挙."""
    r = r_adapter.validate_python(radius)
    q_term = "<-[:DEF]-(:Term)" if only_with_term else ""
    # search_knowde あたりをcallするだけにしたかったが
    # locationを持たせる設計になっているため合わない
    q = f"""
        UNWIND $sent_uids AS sent_uid
        MATCH (sent:Sentence {{uid: sent_uid}})
        // dist=1.. にすることで sent_uidを含めない
        OPTIONAL MATCH p = (sent)-[]-{{1, {r}}}(e:Sentence)
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


async def filter_has_quiz(
    sent_ids: list[UUIDy],
    limit: int,
) -> list[UUID]:
    """クイズが既にある単文を除外."""
    q = """
        UNWIND $sent_uids AS sent_uid
        MATCH (sent:Sentence {{uid: sent_uid}})
        OPTIONAL MATCH (sent)<-[:QUIZ_TARGET]-(q:Quiz)
        WITH sent, COUNT(q) AS quiz_count
        WHERE quiz_count < $limit
        RETURN sent.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "sent_uids": [to_uuid(uid).hex for uid in sent_ids],
            "limit": limit,
        },
    )
    return [row[0] for row in rows]


# 重要な単文を選択肢に混ぜて単純接触効果による学習効果を狙う
async def list_top_scoring_candidates(
    resource_uids: list[UUIDy],
    only_with_term: bool = False,  # noqa: FBT001, FBT002
    order_by=OrderBy(),
    limit: int = 100,
) -> list[UUID]:
    """スコアの上位から候補を出す."""
    rows = await search_knowde_ids(
        "",
        paging=Paging(size=limit),
        order_by=order_by,
        filter_resource_uids=[to_uuid(u).hex for u in resource_uids],
        only_with_term=only_with_term,
    )
    return list(rows)

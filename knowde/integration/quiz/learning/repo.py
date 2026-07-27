"""learning repo."""

from collections.abc import Iterable
from uuid import UUID

from more_itertools import flatten
from neomodel import adb

from knowde.feature.knowde.repo.clause import OrderBy
from knowde.feature.knowde.repo.cypher import q_stats
from knowde.shared.types import UUIDy, to_uuid


async def _resource2ids(q: str, resource_id: UUIDy) -> Iterable[UUID]:
    rows, _ = await adb.cypher_query(
        q,
        params={"resource_id": to_uuid(resource_id).hex},
    )
    return flatten(rows)


async def fetch_uncoverd_sent_ids(
    resource_id: UUIDy,
) -> Iterable[UUID]:
    """未クイズの単文を取得."""
    q = """
        MATCH (s: Sentence {resource_uid: $resource_id})
        WHERE NOT EXISTS {
            MATCH (:Quiz)-[:QUIZ_TARGET]->(s)
        }
        RETURN s.uid
    """
    return await _resource2ids(q, resource_id)


async def fetch_covered_sent_ids(
    resource_id: UUIDy,
) -> Iterable[UUID]:
    """クイズを持つ単文を取得."""
    q = """
        MATCH (s: Sentence {resource_uid: $resource_id})
            <-[:QUIZ_TARGET]->(:Quiz)
        RETURN s.uid
    """
    return await _resource2ids(q, resource_id)


# covered uncoveredと組み合わせる
async def fetch_sort_by_score(
    sent_ids: Iterable[UUID],
) -> list[UUID]:
    """score順に並び替える."""
    order_by = OrderBy()
    q = f"""
        UNWIND $uids AS uid
        MATCH (sent: Sentence {{uid: uid}})
        {q_stats("sent", order_by)}
        {(order_by.phrase())}
        RETURN
            sent.uid AS sent_uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"uids": [to_uuid(uid).hex for uid in sent_ids]},
    )
    return list(flatten(rows))


# async def fetch_quiz_stats(
#     resource_id: UUIDy,
#     user_id: UUIDy,
#     quiz_type: QuizType,
#     now: datetime | None = None,
# ):
#     """クイズの統計情報を取得."""

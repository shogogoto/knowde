"""learning repo."""

from collections.abc import Iterable
from random import Random, SystemRandom
from uuid import UUID

from more_itertools import flatten
from neomodel import adb

from knowde.feature.knowde.repo.clause import OrderBy
from knowde.feature.knowde.repo.cypher import q_stats
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import (
    QuizCoverage,
    QuizTargetOrder,
    QuizTargetPool,
)
from knowde.shared.types import UUIDy, to_uuid


async def _fetch_coverage_sent_ids(
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
    *,
    covered: bool,
) -> list[UUID]:
    """coverage条件に合う単文IDを取得."""
    eligible = "<-[:DEF]-(:Term)" if quiz_type.has_term else ""
    not_ = "" if covered else "NOT "
    q = f"""
        MATCH (sent: Sentence {{resource_uid: $resource_id}})
            {eligible}
        WHERE {not_}EXISTS {{
            MATCH (user: User {{uid: $user_id}})
                -[:CREATE]->(quiz: Quiz {{
                    quiz_type: $quiz_type,
                    is_link_broken: false
                }})-[:QUIZ_TARGET]->(sent)
        }}
        RETURN DISTINCT sent.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "resource_id": to_uuid(resource_id).hex,
            "user_id": to_uuid(user_id).hex,
            "quiz_type": quiz_type.name,
        },
    )
    return list(flatten(rows))


async def fetch_uncovered_sent_ids(
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
) -> list[UUID]:
    """ユーザー向けの有効なクイズがない適格単文を取得."""
    return await _fetch_coverage_sent_ids(
        resource_id,
        user_id,
        quiz_type,
        covered=False,
    )


async def fetch_covered_sent_ids(
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
) -> list[UUID]:
    """ユーザー向けの有効なクイズを持つ適格単文を取得."""
    return await _fetch_coverage_sent_ids(
        resource_id,
        user_id,
        quiz_type,
        covered=True,
    )


# covered uncoveredと組み合わせる
async def fetch_sort_by_score(
    sent_ids: Iterable[UUID],
    *,
    desc: bool = True,
    limit: int | None = None,
) -> list[UUID]:
    """score順に並び替える."""
    if limit is not None and limit < 0:
        msg = "limitは0以上を指定してください"
        raise ValueError(msg)

    order_by = OrderBy(desc=desc)
    limit_clause = "" if limit is None else "LIMIT $limit"
    q = f"""
        UNWIND $uids AS uid
        MATCH (sent: Sentence {{uid: uid}})
        {q_stats("sent", order_by)}
        RETURN
            sent.uid AS sent_uid
        {(order_by.phrase())}
            , sent.uid ASC
        {limit_clause}
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "uids": [to_uuid(uid).hex for uid in sent_ids],
            "limit": limit,
        },
    )
    return list(flatten(rows))


async def fetch_target_ids(  # noqa: PLR0917
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
    pool: QuizTargetPool,
    order: QuizTargetOrder,
    limit: int,
    *,
    rng: Random | None = None,
) -> list[UUID]:
    """指定した母集団から順序と件数を指定してクイズ対象を取得."""
    if limit < 0:
        msg = "limitは0以上を指定してください"
        raise ValueError(msg)

    match pool:
        case QuizTargetPool.UNCOVERED:
            ids = await fetch_uncovered_sent_ids(resource_id, user_id, quiz_type)
        case QuizTargetPool.COVERED:
            ids = await fetch_covered_sent_ids(resource_id, user_id, quiz_type)

    match order:
        case QuizTargetOrder.HIGH_SCORE:
            ids = await fetch_sort_by_score(ids, limit=limit)
        case QuizTargetOrder.LOW_SCORE:
            ids = await fetch_sort_by_score(ids, desc=False, limit=limit)
        case QuizTargetOrder.RANDOM:
            random = rng if rng is not None else SystemRandom()
            ids = random.sample(ids, k=min(limit, len(ids)))

    return ids


async def fetch_coverage(
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
) -> QuizCoverage:
    """クイズ化された単文の割合."""
    eligible = "<-[:DEF]-(:Term)" if quiz_type.has_term else ""
    q = f"""
        MATCH (sent: Sentence {{resource_uid: $resource_id}})
            {eligible}
        OPTIONAL MATCH (user: User {{uid: $user_id}})
            -[:CREATE]->(quiz: Quiz {{
                quiz_type: $quiz_type,
                is_link_broken: false
            }})-[:QUIZ_TARGET]->(sent)
        RETURN
            COUNT(DISTINCT sent) AS eligible,
            COUNT(DISTINCT CASE WHEN quiz IS NOT NULL THEN sent END) AS covered
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "resource_id": to_uuid(resource_id).hex,
            "user_id": to_uuid(user_id).hex,
            "quiz_type": quiz_type.name,
        },
    )
    eligible_count, covered_count = rows[0]
    return QuizCoverage(
        resource_id=to_uuid(resource_id),
        user_id=to_uuid(user_id),
        quiz_type=quiz_type,
        eligible=eligible_count,
        covered=covered_count,
    )


# async def fetch_quiz_stats(
#     resource_id: UUIDy,
#     user_id: UUIDy,
#     quiz_type: QuizType,
#     now: datetime | None = None,
# ):
#     """クイズの統計情報を取得."""

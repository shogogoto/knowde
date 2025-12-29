"""クイズ関連.

時系列順
回答が多い順
正答率が低い順など
"""

from collections.abc import Iterable

from neomodel import adb

from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.collections import (
    ReadableQuizCollection,
    ReadableQuizResult,
)
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.cypher import Paging
from knowde.shared.types import UUIDy, to_uuid


async def list_quiz_by_user_ids(
    user_uids: Iterable[UUIDy],
    paging: Paging = Paging(),
) -> ReadableQuizResult:
    """特定ユーザーのクイズを列挙する."""
    q = f"""
        UNWIND $user_uids AS user_uid
        MATCH (u: User {{uid: user_uid}})
        MATCH(quiz: Quiz)<-[:CREATE]-(u)
        // 新しい順
        ORDER BY quiz.created DESC
        WITH COLLECT(quiz.uid) as quiz_ids
        {paging.return_stmt("quiz_ids")}
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "user_uids": [to_uuid(uid).hex for uid in user_uids],
            **paging.params,
        },
    )
    total, ids = rows[0]
    srcs = await restore_quiz_sources(ids)
    return ReadableQuizResult(
        data=ReadableQuizCollection(root=[build_readable(src) for src in srcs]),
        total=total,
    )


async def list_quiz_by_sentence_ids(
    sent_uids: Iterable[UUIDy],
    paging: Paging = Paging(),
) -> ReadableQuizResult:
    """特定単文に紐づくクイズを列挙する."""
    q = f"""
        UNWIND $sent_uids AS sent_uid
        MATCH (s: Sentence {{uid: sent_uid}})
        MATCH(quiz: Quiz)-[:QUIZ_TARGET]->(s)
        // 新しい順
        ORDER BY quiz.created DESC
        WITH COLLECT(quiz.uid) as quiz_ids
        {paging.return_stmt("quiz_ids")}
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "sent_uids": [to_uuid(uid).hex for uid in sent_uids],
            **paging.params,
        },
    )
    total, ids = rows[0]
    srcs = await restore_quiz_sources(ids)
    return ReadableQuizResult(
        data=ReadableQuizCollection(root=[build_readable(src) for src in srcs]),
        total=total,
    )


async def list_quiz_by_optioned(quiz_uid: UUIDy):
    """クイズのオプションにあるクイズを列挙する."""


# async def list_quiz_by_selected():
#     """."""

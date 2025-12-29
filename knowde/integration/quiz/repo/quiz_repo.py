"""クイズ関連.

時系列順
回答が多い順
正答率が低い順など
"""

from more_itertools import flatten
from neomodel import adb

from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.types import UUIDy, to_uuid


async def list_quiz_by_user_id(user_uid: UUIDy) -> list[ReadableQuiz]:
    """特定ユーザーのクイズを列挙する."""
    q = """
        MATCH (u: User {uid: $user_uid})
        OPTIONAL MATCH(quiz: Quiz)<-[:CREATE]-(u)
        // 新しい順
        ORDER BY quiz.created DESC
        RETURN quiz.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"user_uid": to_uuid(user_uid).hex},
    )
    ids = flatten(rows)
    srcs = await restore_quiz_sources(ids)
    return [build_readable(src) for src in srcs]


async def list_quiz_by_sentence_id(sent_uid: UUIDy) -> list[ReadableQuiz]:
    """特定単文に紐づくクイズを列挙する."""
    q = """
        MATCH (u: User {uid: $user_uid})
        OPTIONAL MATCH(quiz: Quiz)<-[:CREATE]-(u)
        // 新しい順
        ORDER BY quiz.created DESC
        RETURN quiz.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"user_uid": to_uuid(sent_uid).hex},
    )
    ids = flatten(rows)
    srcs = await restore_quiz_sources(ids)
    return [build_readable(src) for src in srcs]


# async def list_quiz_by_selected():
#     """."""

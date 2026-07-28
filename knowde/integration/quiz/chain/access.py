"""QuizChainのアクセス判定."""

from uuid import UUID

from neomodel import adb

from knowde.shared.types import UUIDy, to_uuid


async def can_read_quiz(user_id: UUIDy, quiz_id: UUIDy) -> bool:
    """ユーザーの学習対象Quizか."""
    q = """
        MATCH (:User {uid: $user_id})-[:LEARN]->(:Quiz {uid: $quiz_id})
        RETURN count(*) > 0
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "user_id": to_uuid(user_id).hex,
            "quiz_id": to_uuid(quiz_id).hex,
        },
    )
    return bool(rows[0][0])


async def can_read_sentence(user_id: UUIDy, sentence_id: UUIDy) -> bool:
    """所有resourceまたは学習対象Quizを通じてSentenceを閲覧できるか."""
    q = """
        MATCH (sentence: Sentence {uid: $sentence_id})
        OPTIONAL MATCH
            (:Resource {uid: sentence.resource_uid})-[:OWNED]->(
                owner: User {uid: $user_id}
            )
        OPTIONAL MATCH
            (learner: User {uid: $user_id})-[:LEARN]->(:Quiz)
                -[:QUIZ_TARGET|QUIZ_OPTION|CORRECT]->(sentence)
        RETURN owner IS NOT NULL OR learner IS NOT NULL
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "user_id": to_uuid(user_id).hex,
            "sentence_id": to_uuid(sentence_id).hex,
        },
    )
    return bool(rows and rows[0][0])


async def filter_readable_quiz_ids(
    user_id: UUIDy,
    quiz_ids: list[UUIDy],
) -> list[UUID]:
    """Quiz IDをユーザーの学習対象だけに絞る."""
    q = """
        UNWIND $quiz_ids AS quiz_id
        MATCH (:User {uid: $user_id})-[:LEARN]->(quiz: Quiz {uid: quiz_id})
        RETURN quiz.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "user_id": to_uuid(user_id).hex,
            "quiz_ids": [to_uuid(quiz_id).hex for quiz_id in quiz_ids],
        },
    )
    return [to_uuid(row[0]) for row in rows]

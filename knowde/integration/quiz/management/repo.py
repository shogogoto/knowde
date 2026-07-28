"""Quiz管理repo."""

from neomodel import adb

from knowde.shared.types import UUIDy, to_uuid


async def delete_created_quiz(
    quiz_id: UUIDy,
    user_id: UUIDy,
) -> bool:
    """作成者本人のQuizと、それに対するAnswerを削除."""
    q = """
        MATCH (:User {uid: $user_id})-[:CREATE]->(quiz: Quiz {uid: $quiz_id})
        OPTIONAL MATCH (answer: Answer)-[:ANSWER_OF]->(quiz)
        WITH quiz, [answer IN COLLECT(answer) WHERE answer IS NOT NULL] AS answers
        FOREACH (answer IN answers | DETACH DELETE answer)
        DETACH DELETE quiz
        RETURN 1 AS deleted
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_id": to_uuid(quiz_id).hex,
            "user_id": to_uuid(user_id).hex,
        },
    )
    return bool(rows)

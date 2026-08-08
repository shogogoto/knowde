"""クイズの学習者割り当てrepo."""

from neomodel import adb

from knowde.feature.primitive.types import UUIDy, to_uuid


async def assign_quiz_to_learner(
    quiz_id: UUIDy,
    learner_user_id: UUIDy,
) -> bool:
    """既存クイズをユーザーの学習対象に追加."""
    q = """
        MATCH
            (user: User {uid: $user_id}),
            (quiz: Quiz {uid: $quiz_id})
        MERGE (user)-[:LEARN]->(quiz)
        RETURN quiz.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_id": to_uuid(quiz_id).hex,
            "user_id": to_uuid(learner_user_id).hex,
        },
    )
    return bool(rows)

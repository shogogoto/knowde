"""Quiz管理repo."""

from neomodel import adb

from knowde.feature.entry.mapper import MResource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.management.domain import QuizResourceStatus
from knowde.shared.types import UUIDy, to_uuid


async def list_created_quiz_resource_statuses(
    user_id: UUIDy,
) -> list[QuizResourceStatus]:
    """作成済みQuizをResourceごとに集計."""
    q = """
        MATCH (:User {uid: $user_id})-[:CREATE]->(quiz: Quiz)
            -[:QUIZ_TARGET]->(target: Sentence)
        MATCH (resource: Resource {uid: target.resource_uid})
        WITH resource, quiz.quiz_type AS quiz_type, COUNT(quiz) AS count,
            MAX(quiz.created) AS type_last_created
        ORDER BY quiz_type
        WITH resource,
            COLLECT([quiz_type, count]) AS counts,
            SUM(count) AS total,
            MAX(type_last_created) AS last_created
        ORDER BY last_created DESC, resource.title
        RETURN resource, counts, total, last_created
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"user_id": to_uuid(user_id).hex},
    )
    return [
        QuizResourceStatus(
            resource=MResource.freeze_dict(resource),
            quiz_counts={
                QuizType(quiz_type.lower()): count for quiz_type, count in counts
            },
            total_quizzes=total,
            last_created_at=last_created,
        )
        for resource, counts, total, last_created in rows
    ]


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

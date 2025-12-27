"""ロジックを含まないコアなrepo."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID, uuid4

from neomodel import adb

from knowde.integration.quiz.domain.domain import (
    QuizType,
)
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.util import TZ


# idを渡すだけでロジックは分離
async def create_quiz(  # noqa: PLR0917
    target_sent_uid: UUIDy,
    statement_type: QuizType,
    option_uids: Sequence[UUIDy],
    correct_uids: Sequence[UUIDy] | None = None,
    now: datetime | None = None,
    quiz_uid: UUID | None = None,
    user_uid: UUIDy | None = None,
) -> UUID:
    """クイズの永続化."""
    if now is None:
        now = datetime.now(tz=TZ)
    if quiz_uid is None:
        quiz_uid = uuid4()
    if correct_uids is None:
        correct_uids = []
    q = """
        MATCH (tgt: Sentence {uid: $target_uid})
        CREATE (quiz: Quiz {
            uid: $quiz_uid
            , statement_type: $statement_type
            , is_link_broken: false
            , created: datetime($now)
        })-[:QUIZ_TARGET]->(tgt)
        WITH quiz
        CALL (quiz) {
            OPTIONAL MATCH (u: User {uid: $user_uid})
            WITH quiz, u WHERE u IS NOT NULL
            CREATE (u)-[:CREATE]->(quiz)
        }
        WITH quiz
        UNWIND $option_uids AS ouid
        MATCH (opt: Sentence {uid: ouid})
        CREATE (quiz)-[:QUIZ_OPTION]->(opt)
        WITH quiz
        UNWIND $correct_uids AS cuid
        MATCH (c: Sentence {uid: cuid})
        CREATE (quiz)-[:CORRECT]->(c)
    """
    _rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_uid": quiz_uid.hex,
            "target_uid": to_uuid(target_sent_uid).hex,
            "option_uids": [to_uuid(u).hex for u in option_uids],
            "correct_uids": [to_uuid(u).hex for u in correct_uids],
            "statement_type": statement_type.name,
            "user_uid": to_uuid(user_uid).hex if user_uid is not None else None,
            "now": now.isoformat(),
        },
    )
    return quiz_uid


async def create_answer(  # noqa: PLR0917
    quiz_uid: UUID,
    selected_uids: Sequence[UUIDy],
    is_correct: bool,  # noqa: FBT001
    user_uid: UUIDy,  # 回答者idは必須にする。回答したければユーザー登録しろ、という導線
    answer_uid: UUID | None = None,
    now: datetime | None = None,
) -> UUID:
    """回答の永続化.

    クイズを指す
    """
    if answer_uid is None:
        answer_uid = uuid4()
    if now is None:
        now = datetime.now(tz=TZ)

    q = """
        MATCH (quiz: Quiz {uid: $quiz_uid})
            , (u: User {uid: $user_uid})
        CREATE (ans: Answer {
            uid: $answer_uid
            , created: datetime($now)
            , is_correct: $is_correct
        })-[:ANSWER_OF]->(quiz)
            , (ans)<-[:ANSWER]-(u)
        WITH ans
        UNWIND $selected_uids AS suid
        MATCH (s: Sentence {uid: suid})
        CREATE (ans)-[:SELECT]->(s)
        RETURN ans
    """
    _rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_uid": quiz_uid.hex,
            "selected_uids": [to_uuid(u).hex for u in selected_uids],
            "answer_uid": answer_uid.hex,
            "now": now.isoformat(),
            "is_correct": is_correct,
            "user_uid": to_uuid(user_uid).hex,
        },
    )
    return answer_uid

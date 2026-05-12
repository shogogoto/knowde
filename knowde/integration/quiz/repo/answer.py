"""回答repo."""

from datetime import datetime
from uuid import UUID, uuid4

from neomodel import adb

from knowde.integration.quiz.domain.answer import Answer
from knowde.integration.quiz.domain.build import build_readable_quiz
from knowde.integration.quiz.errors import AnswerFailedError
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.util import TZ


async def fetch_is_correct(quiz_uid: UUID, selected_uids: list[str]) -> bool:
    """クイズの回答の正解・不正解の問い合わせ."""
    srcs = await restore_quiz_sources([quiz_uid])
    rq = build_readable_quiz(srcs[0])
    return rq.is_correct(selected_uids)


async def create_answer(
    quiz_uid: UUID,
    selected_uids: list[str],
    user_uid: UUIDy,  # 回答者idは必須にする。回答したければユーザー登録しろ、という導線
) -> Answer:
    """回答の永続化."""
    answer_uid = uuid4()
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
        WITH ans, u
        UNWIND $selected_uids AS suid
        MATCH (s: Sentence {uid: suid})
        CREATE (ans)-[:SELECT]->(s)
        RETURN ans, u
    """

    is_correct = await fetch_is_correct(quiz_uid, selected_uids)
    rows, _ = await adb.cypher_query(
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

    for row in rows:
        _, u = row
        return Answer(
            answer_uid=answer_uid,
            quiz_uid=quiz_uid,
            selected=selected_uids,
            who=u.get("uid"),
            is_correct=is_correct,
            created=now,
        )

    msg = "回答の永続化失敗"
    raise AnswerFailedError(msg)

"""回答関連repo."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID, uuid4

from neomodel import adb

from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.util import TZ


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


async def list_answers_by_quiz(quiz_uid: UUIDy):
    """クイズのフィードバックとして回答を取得する.

    正答率や何を選んで誤答してしまったかなど
        それぞれの選択率
    """

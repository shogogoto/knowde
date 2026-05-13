"""ロジックを含まないコアなrepo."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID, uuid4

from neomodel import adb

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.distractor import fetch_distractor_ids
from knowde.integration.quiz.domain.domain import (
    QuizSource,
    QuizType,
    ReadableQuiz,
)
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.util import TZ


async def create_quiz_and_correct(
    target_sent_uid: UUIDy,
    quiz_type: QuizType,
    option_uids: Sequence[UUIDy],
    user_uid: UUIDy,  # 誰が作ったか
    correct_uids: Sequence[UUIDy] | None = None,
) -> UUID:
    """クイズとその正解の永続化."""
    now = datetime.now(tz=TZ)
    quiz_uid = uuid4()
    if correct_uids is None:
        correct_uids = []
    q = """
        MATCH (tgt: Sentence {uid: $target_uid})
        CREATE (quiz: Quiz {
            uid: $quiz_uid
            , quiz_type: $quiz_type
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
        WITH DISTINCT quiz
        UNWIND  $correct_uids AS cuid
        MATCH (c: Sentence {uid: cuid})
        CREATE (quiz)-[:CORRECT]->(c)
    """
    _, _ = await adb.cypher_query(
        q,
        params={
            "quiz_uid": quiz_uid.hex,
            "target_uid": to_uuid(target_sent_uid).hex,
            "option_uids": [to_uuid(u).hex for u in option_uids],
            "correct_uids": [to_uuid(u).hex for u in correct_uids],
            "quiz_type": quiz_type.name,
            "user_uid": to_uuid(user_uid).hex if user_uid is not None else None,
            "now": now.isoformat(),
        },
    )
    return quiz_uid


# 誤答肢が足りなくて失敗することがあるので
# retryをできるようにしたい
# 正解の数が決め打ちになっているのを直したい
async def generate_quiz(  # noqa: PLR0917
    qt: QuizType,
    ct: CandidateType,
    target_sent_uid: UUIDy,
    n_option: int,
    user_id: UUIDy,
    correct_sent_uids: Sequence[UUIDy] | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002 for debug
) -> tuple[ReadableQuiz, QuizSource]:
    """高級なクイズ生成."""
    ds = await fetch_distractor_ids(
        [target_sent_uid],
        ct,
        n_option - 1,  # 正解の数を除く
        qt.has_term,
    )
    quiz_id = await create_quiz_and_correct(
        target_sent_uid,
        qt,
        ds,
        user_uid=user_id,
        correct_uids=correct_sent_uids,
    )
    srcs = await restore_quiz_sources([quiz_id])
    src = srcs[0]
    rq = src.to_readable()
    if do_print:
        print(rq.string)  # noqa: T201
    return rq, src

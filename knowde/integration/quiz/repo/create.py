"""ロジックを含まないコアなrepo."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID, uuid4

from neomodel import adb

from knowde.integration.quiz.domain.answer import Answer
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.domain import (
    QuizType,
)
from knowde.integration.quiz.errors import AnswerFailedError
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.util import TZ


async def create_quiz_and_correct(  # noqa: PLR0917
    target_sent_uid: UUIDy,
    quiz_type: QuizType,
    option_uids: Sequence[UUIDy],
    correct_uids: Sequence[UUIDy] | None = None,
    now: datetime | None = None,
    quiz_uid: UUID | None = None,
    user_uid: UUIDy | None = None,
) -> UUID:
    """クイズとその正解の永続化."""
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
    _rows, _ = await adb.cypher_query(
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


# populate 定住させる
#  IT で空のDBにデータを流し込むというニュアンス
async def populate_quiz(
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
    n_quiz: int,
    now: datetime | None = None,
):
    """coverageを上げるためのクイズ一括作成.

    リソースごとの学習度を見て一括でクイズを作ったりしたいかも
    テキトーにクイズを新規作成する
    score順
    リソース全体から無作為に選ぶ
    クイズ未作成の単文の内から選ぶ
    正答率が低いものから選ぶ
      回答管理が優先
    chainを辿ったクイズ一括作成.

    全く同じクイズを重複して作成できないようにする
    """
    if now is None:
        now = datetime.now(tz=TZ)
    # must_has_term = quiz_type in {QuizType.SENT2TERM, QuizType.TERM2SENT}
    # resoure のハイスコア順に sent_ids を取得
    # tgt_uids = await list_top_scoring_candidates(
    #     resource_id,
    #     n_candidate=n_quiz,
    #     must_has_term=must_has_term,
    #     has_quiz=True,
    # )

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

    _rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_type": quiz_type.name,
            # "quiz_uid": quiz_uid.hex,
            # "target_uid": to_uuid(target_sent_uid).hex,
            # "option_uids": [to_uuid(u).hex for u in option_uids],
            # "correct_uids": [to_uuid(u).hex for u in correct_uids],
            # "quiz_type": quiz_type.name,
            # "user_uid": to_uuid(user_uid).hex if user_uid is not None else None,
            "now": now.isoformat(),
        },
    )


async def create_answer(
    quiz_uid: UUID,
    selected_uids: list[str],
    # 回答者idは必須にする。回答したければユーザー登録しろ、という導線
    user_uid: UUIDy,
    answer_uid: UUID | None = None,
    now: datetime | None = None,
) -> Answer:
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
        WITH ans, u
        UNWIND $selected_uids AS suid
        MATCH (s: Sentence {uid: suid})
        CREATE (ans)-[:SELECT]->(s)
        RETURN ans, u
    """

    srcs = await restore_quiz_sources([quiz_uid])
    rq = build_readable(srcs[0])
    is_correct = rq.is_correct(selected_uids)
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

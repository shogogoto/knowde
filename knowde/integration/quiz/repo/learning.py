"""学習度管理."""

from datetime import datetime

from neomodel import adb
from pydantic import BaseModel

from knowde.integration.quiz.domain.parts import QuizType
from knowde.shared.types import UUIDy
from knowde.shared.util import TZ


class ResourceCovoerage(BaseModel, frozen=True):
    """リソースの学習度.

    n_rel_quiz / n_rel
    n_term_quiz / n_term
    n_quiz / n_sent
    """

    rel_coverage: float
    term_coverage: float


# async def fetch_resource_coverage(
#     user_id: UUIDy,
#     resource_id: UUIDy,
# ) -> ResourceCovoerage:
#     """リソースの学習度を取得する."""


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

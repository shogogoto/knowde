"""quiz router.

クイズ作成
    候補検索 repo
        半径
        ハイスコア
        関係から候補を出す
    選択肢サンプリング: 候補から選択肢を選ぶ



クイズ回答
回答一覧
クイズ一覧
対象固定

resourceがある
その中の単文を指定してクイズを作成する
    クイズの種類
    選択肢検索方式
    選択肢の数 n_option

    return 作成した可読クイズ

それを元にして回答する
    回答を保存する

    正解か否かを返す

"""

from uuid import UUID

from fastapi import APIRouter

from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.domain import Answer, ReadableQuiz
from knowde.integration.quiz.repo.create import create_answer
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.router.params import AnswerParam, CreateQuizParam
from knowde.integration.quiz.router.usecase import create_term2sent_quiz_usecase
from knowde.shared.user.router_util import ActiveUser, TrackUser
from knowde.shared.user.schema import UserReadPublic

_r = APIRouter(prefix="/quiz", tags=["quiz"])


@_r.post("")
async def create_quiz_api(
    param: CreateQuizParam,
    user: TrackUser,  # optionalだからTrackUserを使用
) -> ReadableQuiz:
    """クイズを新規作成."""
    return await create_term2sent_quiz_usecase(param, user.uid if user else None)


@_r.post("/answer/{quiz_id}")
async def answer_quiz_api(
    quiz_id: UUID,
    param: AnswerParam,
    user: ActiveUser,
) -> Answer:
    """クイズに回答."""
    srcs = await restore_quiz_sources([quiz_id])
    rq = build_readable(srcs[0])
    is_correct = rq.is_correct(param.selected)
    answer_uid = await create_answer(
        quiz_id,
        param.selected,
        is_correct=is_correct,
        user_uid=user.uid,
    )

    # 正解がどれかや他の選択肢の解説など
    #   クイズチェーンに繋がるような情報も返す
    #   過去の回答も返す(正答率)
    #
    return Answer(
        answer_uid=answer_uid,
        selected=param.selected,
        is_correct=is_correct,
        quiz=rq,
        who=UserReadPublic.model_validate(user.model_dump()),
    )


@_r.get("/{sentence_id}")
async def list_quiz_by_sentence_id(sentence_id: UUID):
    """単文と紐づくクイズ一覧を取得.

    紐づき方はいろいろ
      target
      option
        -> この選択肢は何だろう?と思ったらいろいろ辿れるように
          詳細の確認
          それと紐づくクイズや回答
      answer
    """


def quiz_router() -> APIRouter:  # noqa: D103
    return _r

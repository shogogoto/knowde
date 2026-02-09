"""quiz router."""

from uuid import UUID

from fastapi import APIRouter

from knowde.integration.quiz.answer.domain import Answer
from knowde.integration.quiz.answer.repo import create_answer
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.router.params import (
    AnswerParam,
    CreateQuizParam,
)
from knowde.integration.quiz.router.usecase import create_quiz_uc
from knowde.shared.user.router_util import ActiveUser, TrackUser
from knowde.shared.user.schema import UserReadPublic

_r = APIRouter(prefix="/quiz", tags=["quiz"])


@_r.post("")
async def create_quiz_api(
    param: CreateQuizParam,
    user: TrackUser,  # optionalだからTrackUserを使用
) -> ReadableQuiz:
    """単文指定してクイズを作成."""
    qs = await create_quiz_uc(param, user.uid if user else None)
    return qs.root[0]


# @_r.post("")
# async def batch_create_quiz_api(
#     param: BatchCreateQuizParam,
#     user: TrackUser,  # optionalだからTrackUserを使用
# ) -> ReadableQuiz:
#     """リソースからいい感じにクイズを一括作成."""


# ------------------------------------------------------------------------------
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

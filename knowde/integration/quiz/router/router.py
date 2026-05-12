"""quiz router."""

from uuid import UUID

from fastapi import APIRouter

from knowde.integration.quiz.domain.answer import Answer
from knowde.integration.quiz.domain.collections import ReadableQuizResult
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.repo.answer import create_answer
from knowde.integration.quiz.repo.list_query import list_quiz_by_sentence_ids
from knowde.integration.quiz.router.params import (
    AnswerParam,
    CreateQuizParam,
)
from knowde.integration.quiz.router.usecase import create_quiz_uc
from knowde.shared.user.router_util import ActiveUser, TrackUser

_r = APIRouter(prefix="/quiz", tags=["quiz"])


@_r.post("")
async def create_quiz_api(
    param: CreateQuizParam,
    user: TrackUser,  # optionalだからTrackUserを使用
) -> ReadableQuiz:
    """単文指定してクイズを作成.

    単文を追っている途中で思いつきでクイズを作る
    """
    qs = await create_quiz_uc(param, user.uid if user else None)
    return qs.root[0]


# @_r.post("")
# async def batch_create_quiz_api(
#     param: BatchCreateQuizParam,
#     user: TrackUser,  # optionalだからTrackUserを使用
# ) -> ReadableQuizList:
#     """リソースからいい感じにクイズを一括作成.
#
#     どういうサイクルで使う?
#     リソースの復習度合い、回答状況を見て一括で復習を用意したいときに使えるものが欲しい
#
#     リソース一覧の回答状況を見て全自動でクイズを作ってくれるのもいいな
#     重要で回答がない、または回答が間違っているものを選んで出題してくれる
#     """


@_r.get("/{sentence_id}")
async def list_quiz_by_sentence_id(
    sentence_id: UUID,
) -> ReadableQuizResult:
    """単文と紐づくクイズ一覧を取得."""
    return await list_quiz_by_sentence_ids([sentence_id])


# いろんな条件指定でクイズリストは一本化できるんじゃね?
# sent_id指定、resource指定
@_r.get("")
async def list_quiz():
    """ダッシュボードで."""


# ------------------------------------------------------------------------------
@_r.post("/answer/{quiz_id}")
async def answer_quiz_api(
    quiz_id: UUID,
    param: AnswerParam,
    user: ActiveUser,
) -> Answer:
    """クイズに回答する."""
    return await create_answer(
        quiz_id,
        param.selected,
        user_uid=user.uid,
    )


@_r.get("/answer/{quiz_id}")
async def list_answer(quiz_id: UUID):
    """回答一覧."""


def quiz_router() -> APIRouter:  # noqa: D103
    return _r

"""quiz router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from knowde.feature.entry.errors import NotOwnerError
from knowde.feature.entry.resource.repo.owner import check_entry_owner
from knowde.integration.quiz.answering.repo import create_answer
from knowde.integration.quiz.chain.router import quiz_chain_router
from knowde.integration.quiz.domain.answer import Answer, Answers
from knowde.integration.quiz.domain.collections import ReadableQuizResult
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.integration.quiz.learning.progress.domain import ResourceLearningStatus
from knowde.integration.quiz.learning.progress.usecase import fetch_learning_status
from knowde.integration.quiz.learning.study_plan.router import study_plan_router
from knowde.integration.quiz.listing.repo import (
    list_answers,
    list_learning_quizzes,
)
from knowde.integration.quiz.router.params import (
    AnswerParam,
    CreateQuizParam,
)
from knowde.shared.cypher import Paging
from knowde.shared.user.router_util import ActiveUser

_r = APIRouter(prefix="/quiz", tags=["quiz"])


@_r.post("")
async def create_quiz_api(
    param: CreateQuizParam,
    user: ActiveUser,
) -> ReadableQuiz:
    """単文指定してクイズを作成.

    単文を追っている途中で思いつきでクイズを作る
    """
    src = await generate_quiz(
        param.quiz_type,
        param.cand_type,
        param.target_sent_uid,
        param.n_option,
        user_id=user.uid,
    )
    return src.to_readable()


@_r.get("")
async def list_quiz(
    user: ActiveUser,
    page: Annotated[int, Query(gt=0)] = 1,
    size: Annotated[int, Query(gt=0)] = 100,
) -> ReadableQuizResult:
    """認証ユーザーに用意された学習対象クイズを一覧取得."""
    return await list_learning_quizzes(
        user.uid,
        Paging(page=page, size=size),
    )


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
async def list_answer(
    quiz_id: UUID,
    user: ActiveUser,
) -> Answers:
    """認証ユーザー自身の回答一覧."""
    return await list_answers([quiz_id], user_uid=user.uid)


@_r.get("/learning-progress/{resource_id}")
async def get_learning_progress_api(
    resource_id: UUID,
    user: ActiveUser,
) -> ResourceLearningStatus:
    """所有resourceのクイズ学習進捗を取得."""
    if not await check_entry_owner(user.uid, resource_id):
        msg = "所有していないresourceの学習進捗は取得できません"
        raise NotOwnerError(msg=msg)
    return await fetch_learning_status(resource_id, user.uid)


_r.include_router(study_plan_router())
_r.include_router(quiz_chain_router())


def quiz_router() -> APIRouter:  # noqa: D103
    return _r

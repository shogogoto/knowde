"""QuizChain API."""

from uuid import UUID

from fastapi import APIRouter

from tanbun.feature.quiz.chain.domain import QuizChain
from tanbun.feature.quiz.chain.usecase import (
    expand_quiz_chain,
    expand_sentence_chain,
)
from tanbun.feature.user.router_util import ActiveUser

_router = APIRouter(prefix="/chain", tags=["quiz-chain"])


@_router.get("/quizzes/{quiz_id}")
async def expand_quiz_chain_api(
    quiz_id: UUID,
    user: ActiveUser,
) -> QuizChain:
    """Quizから関連Sentenceへ1ホップ展開."""
    return await expand_quiz_chain(user.uid, quiz_id)


@_router.get("/sentences/{sentence_id}")
async def expand_sentence_chain_api(
    sentence_id: UUID,
    user: ActiveUser,
) -> QuizChain:
    """Sentenceから関連Quizへ1ホップ展開."""
    return await expand_sentence_chain(user.uid, sentence_id)


def quiz_chain_router() -> APIRouter:
    """QuizChain router."""
    return _router

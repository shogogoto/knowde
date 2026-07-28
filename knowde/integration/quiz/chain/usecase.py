"""QuizChainのusecase."""

from knowde.integration.quiz.chain.access import (
    can_read_quiz,
    can_read_sentence,
    filter_readable_quiz_ids,
)
from knowde.integration.quiz.chain.domain import QuizChain
from knowde.integration.quiz.chain.errors import QuizChainNotFoundError
from knowde.integration.quiz.chain.repo import (
    fetch_quiz_chain,
    fetch_related_quiz_ids,
    fetch_sentence_chain,
)
from knowde.shared.types import UUIDy


async def expand_quiz_chain(
    user_id: UUIDy,
    quiz_id: UUIDy,
) -> QuizChain:
    """閲覧可能なQuizからSentenceへ1ホップ展開."""
    if not await can_read_quiz(user_id, quiz_id):
        msg = f"閲覧可能なQuizが見つかりません: {quiz_id}"
        raise QuizChainNotFoundError(msg=msg)

    chain = await fetch_quiz_chain(quiz_id)
    if chain is None:
        msg = f"Quizが見つかりません: {quiz_id}"
        raise QuizChainNotFoundError(msg=msg)
    return chain


async def expand_sentence_chain(
    user_id: UUIDy,
    sentence_id: UUIDy,
) -> QuizChain:
    """閲覧可能なSentenceからQuizへ1ホップ展開."""
    if not await can_read_sentence(user_id, sentence_id):
        msg = f"閲覧可能なSentenceが見つかりません: {sentence_id}"
        raise QuizChainNotFoundError(msg=msg)

    related_ids = await fetch_related_quiz_ids(sentence_id)
    readable_ids = await filter_readable_quiz_ids(user_id, related_ids)
    chain = await fetch_sentence_chain(sentence_id, readable_ids)
    if chain is None:
        msg = f"Sentenceが見つかりません: {sentence_id}"
        raise QuizChainNotFoundError(msg=msg)
    return chain

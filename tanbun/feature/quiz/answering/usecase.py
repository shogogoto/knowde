"""クイズ回答usecase."""

from tanbun.feature.domain.types import UUIDy
from tanbun.feature.quiz.answering.repo import create_answer
from tanbun.feature.quiz.chain.domain import QuizChain
from tanbun.feature.quiz.chain.usecase import expand_quiz_chain


async def answer_quiz_as_chain(
    quiz_id: UUIDy,
    selected: list[str],
    user_id: UUIDy,
) -> QuizChain:
    """回答を保存し、その結果を含むQuizChainを返す."""
    chain = await expand_quiz_chain(user_id, quiz_id)
    answer = await create_answer(quiz_id, selected, user_uid=user_id)
    return chain.model_copy(update={"answers": [answer]})

"""QuizChain usecaseのテスト."""

import pytest

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.domain.types import to_uuid
from tanbun.feature.quiz.candidate.types import CandidateType
from tanbun.feature.quiz.chain.errors import QuizChainNotFoundError
from tanbun.feature.quiz.chain.usecase import (
    expand_quiz_chain,
    expand_sentence_chain,
)
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.fixture import fx_u
from tanbun.feature.quiz.generation.repo import generate_quiz
from tanbun.feature.tanbun.label import LSentence
from tanbun.feature.user.label import LUser
from tanbun.feature.user.testing import aregister

u = async_fixture()(fx_u)


@mark_async_test()
async def test_expand_sentence_chain_one_hop(u: LUser):
    """Sentenceから本人のQuizだけを取得し、他のSentenceへは展開しない."""
    target = await LSentence.nodes.first(val="ccc")
    own = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        5,
        u.uid,
    )
    other = await aregister(email="quiz-chain-other@ex.com")
    await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        5,
        other.uid,
    )

    chain = await expand_sentence_chain(u.uid, target.uid)

    assert [tanbun.uid for tanbun in chain.sentences] == [
        to_uuid(target.uid),
    ]
    assert [quiz.quiz_id for quiz in chain.quizzes] == [own.quiz_id]
    assert {link.sentence_id for link in chain.links} == {
        to_uuid(target.uid),
    }


@mark_async_test()
async def test_reject_unassigned_quiz_chain(u: LUser):
    """LEARNがないQuizは展開できない."""
    target = await LSentence.nodes.first(val="ccc")
    other = await aregister(email="quiz-chain-owner@ex.com")
    quiz = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        5,
        other.uid,
    )

    with pytest.raises(QuizChainNotFoundError):
        await expand_quiz_chain(u.uid, quiz.quiz_id)

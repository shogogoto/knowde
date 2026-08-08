"""QuizChain repoのテスト."""

import pytest

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.domain.types import to_uuid
from tanbun.feature.quiz.candidate.types import CandidateType
from tanbun.feature.quiz.chain.domain import QuizChainRole
from tanbun.feature.quiz.chain.repo import fetch_quiz_chain
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.domain.rel import QuizRel
from tanbun.feature.quiz.fixture import fx_u
from tanbun.feature.quiz.generation.repo import generate_quiz
from tanbun.feature.tanbun.label import LSentence
from tanbun.feature.user.label import LUser

u = async_fixture()(fx_u)


@pytest.mark.parametrize("quiz_type", list(QuizType))
@mark_async_test()
async def test_fetch_quiz_chain(quiz_type: QuizType, u: LUser):
    """全quiz typeを表示できるTanbunと知識関係を1ホップ取得."""
    target = LSentence.nodes.first(val="ccc")
    pair = LSentence.nodes.first(val="parent")
    source = await generate_quiz(
        quiz_type,
        CandidateType.ALL,
        target.uid,
        3,
        u.uid,
        correct_sent_uids=[pair.uid] if not quiz_type.has_term else None,
    )

    chain = await fetch_quiz_chain(source.quiz_id)

    assert chain is not None
    assert [quiz.quiz_id for quiz in chain.quizzes] == [source.quiz_id]
    assert {tanbun.uid for tanbun in chain.sentences} == {
        to_uuid(sentence_id) for sentence_id in source.sources
    }
    target_tanbun = next(
        tanbun for tanbun in chain.sentences if tanbun.uid == to_uuid(source.target_id)
    )
    assert target_tanbun.term is not None
    assert target_tanbun.sentence == "ccc"

    target_roles = {
        link.role
        for link in chain.links
        if link.sentence_id == to_uuid(source.target_id)
    }
    if quiz_type.has_term:
        assert target_roles == {
            QuizChainRole.TARGET,
            QuizChainRole.CORRECT,
        }
    else:
        assert target_roles == {QuizChainRole.TARGET}
        correct_link = next(
            link
            for link in chain.links
            if link.sentence_id == to_uuid(source.correct_ids[0])
            and link.role is QuizChainRole.CORRECT
        )
        assert correct_link.relations == [QuizRel.PARENT]

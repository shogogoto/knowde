"""QuizChain repoのテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.knowde.label import LSentence
from knowde.feature.primitive.types import to_uuid
from knowde.feature.quiz.candidate.types import CandidateType
from knowde.feature.quiz.chain.domain import QuizChainRole
from knowde.feature.quiz.chain.repo import fetch_quiz_chain
from knowde.feature.quiz.domain.parts import QuizType
from knowde.feature.quiz.domain.rel import QuizRel
from knowde.feature.quiz.fixture import fx_u
from knowde.feature.quiz.generation.repo import generate_quiz
from knowde.feature.user.label import LUser

u = async_fixture()(fx_u)


@pytest.mark.parametrize("quiz_type", list(QuizType))
@mark_async_test()
async def test_fetch_quiz_chain(quiz_type: QuizType, u: LUser):
    """全quiz typeを表示できるKnowdeと知識関係を1ホップ取得."""
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
    assert {knowde.uid for knowde in chain.sentences} == {
        to_uuid(sentence_id) for sentence_id in source.sources
    }
    target_knowde = next(
        knowde for knowde in chain.sentences if knowde.uid == to_uuid(source.target_id)
    )
    assert target_knowde.term is not None
    assert target_knowde.sentence == "ccc"

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

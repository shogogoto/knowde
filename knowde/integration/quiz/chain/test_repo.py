"""QuizChain repoのテスト."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.chain.domain import QuizChainRole
from knowde.integration.quiz.chain.repo import fetch_quiz_chain
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import to_uuid
from knowde.shared.user.label import LUser

u = async_fixture()(fx_u)


@mark_async_test()
async def test_fetch_quiz_chain(u: LUser):
    """Quizとtarget・option・correct Sentenceを1ホップ取得."""
    target = LSentence.nodes.first(val="ccc")
    source = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        5,
        u.uid,
    )

    chain = await fetch_quiz_chain(source.quiz_id)

    assert chain is not None
    assert [quiz.quiz_id for quiz in chain.quizzes] == [source.quiz_id]
    assert {sentence.sentence_id for sentence in chain.sentences} == {
        to_uuid(sentence_id) for sentence_id in source.sources
    }
    target_roles = {
        link.role
        for link in chain.links
        if link.sentence_id == to_uuid(source.target_id)
    }
    assert target_roles == {
        QuizChainRole.TARGET,
        QuizChainRole.CORRECT,
    }

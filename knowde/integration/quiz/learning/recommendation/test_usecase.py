"""複数リソースを横断するクイズ推薦のテスト."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.fixture import (
    create_learning_test_resource,
    fx_learning,
    generate_test_quizzes,
    learning_resource_id,
)
from knowde.integration.quiz.learning.recommendation.usecase import (
    recommend_quizzes,
)
from knowde.shared.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_recommend_quizzes_round_robin(u: LUser):
    """入力順を優先して複数リソースから均等に推薦."""
    first = await learning_resource_id(u.uid)
    second = await create_learning_test_resource(u.uid)
    n_quiz = 3

    recommendations = await recommend_quizzes(
        [first, second],
        u.uid,
        QuizType.TERM2SENT,
        CandidateType.ALL,
        n_quiz=n_quiz,
        n_option=3,
    )

    assert [item.resource_id for item in recommendations] == [
        first,
        second,
        first,
    ]
    assert len({item.quiz.quiz_id for item in recommendations}) == n_quiz


@mark_async_test()
async def test_recommend_quizzes_only_from_selected_resources(u: LUser):
    """提案対象として渡していないリソースは推薦しない."""
    await learning_resource_id(u.uid)
    selected = await create_learning_test_resource(u.uid)
    n_quiz = 2

    recommendations = await recommend_quizzes(
        [selected],
        u.uid,
        QuizType.TERM2SENT,
        CandidateType.ALL,
        n_quiz=n_quiz,
        n_option=3,
    )

    assert len(recommendations) == n_quiz
    assert {item.resource_id for item in recommendations} == {selected}


@mark_async_test()
async def test_recommend_existing_unattempted_quiz_first(u: LUser):
    """新規生成より既存の未回答クイズを優先."""
    resource_id = await learning_resource_id(u.uid)
    existing = (await generate_test_quizzes(resource_id, u.uid, 1))[0]

    recommendations = await recommend_quizzes(
        [resource_id],
        u.uid,
        QuizType.TERM2SENT,
        CandidateType.ALL,
        n_quiz=1,
        n_option=3,
    )

    assert recommendations[0].quiz.quiz_id == existing.quiz_id

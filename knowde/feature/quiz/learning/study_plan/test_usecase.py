"""StudyPlanのユースケーステスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.quiz.domain.parts import QuizType
from knowde.feature.quiz.learning.fixture import (
    create_learning_test_resource,
    fx_learning,
    learning_resource_id,
)
from knowde.feature.quiz.learning.study_plan.domain import StudyPlanDraft
from knowde.feature.quiz.learning.study_plan.errors import (
    StudyPlanNotFoundError,
)
from knowde.feature.quiz.learning.study_plan.repo import create_study_plan
from knowde.feature.quiz.learning.study_plan.usecase import (
    recommend_quizzes_for_study_plan,
)
from knowde.feature.user.label import LUser
from knowde.feature.user.testing import aregister

u = async_fixture()(fx_learning)
MIN_RECOMMENDED_OPTIONS = 2


@mark_async_test()
async def test_recommend_quizzes_for_study_plan(u: LUser):
    """保存したresource順と設定でクイズを推薦."""
    first = await learning_resource_id(u.uid)
    second = await create_learning_test_resource(u.uid)
    plan = await create_study_plan(
        u.uid,
        StudyPlanDraft(
            name="毎日の学習",
            resource_ids=[first, second],
            quiz_types=[QuizType.TERM2SENT, QuizType.SENT2TERM],
            n_quiz=3,
            n_option=3,
        ),
    )

    recommendations = await recommend_quizzes_for_study_plan(
        plan.uid,
        u.uid,
    )

    assert [item.resource_id for item in recommendations] == [
        first,
        first,
        second,
    ]
    assert len({item.quiz.quiz_id for item in recommendations}) == plan.n_quiz
    assert {item.quiz.quiz_type for item in recommendations} == {
        QuizType.TERM2SENT,
        QuizType.SENT2TERM,
    }

    other = await aregister(email="study-plan-reader@ex.com")
    with pytest.raises(StudyPlanNotFoundError):
        await recommend_quizzes_for_study_plan(plan.uid, other.uid)


@mark_async_test()
async def test_recommend_quizzes_across_all_quiz_types(u: LUser):
    """自動生成できるQuizTypeを、関係QuizTypeと同時選択しても推薦する."""
    resource_id = await learning_resource_id(u.uid)
    plan = await create_study_plan(
        u.uid,
        StudyPlanDraft(
            name="全形式",
            resource_ids=[resource_id],
            quiz_types=[
                QuizType.TERM2SENT,
                QuizType.SENT2TERM,
                QuizType.REL2PAIR,
                QuizType.PAIR2REL,
            ],
            n_quiz=1,
            n_option=4,
        ),
    )

    recommendations = await recommend_quizzes_for_study_plan(plan.uid, u.uid)

    assert [item.quiz.quiz_type for item in recommendations] == [
        QuizType.TERM2SENT,
        QuizType.SENT2TERM,
        QuizType.REL2PAIR,
        QuizType.PAIR2REL,
    ]
    pair2rel = recommendations[-1].quiz.to_readable()
    assert MIN_RECOMMENDED_OPTIONS <= len(pair2rel.options) <= plan.n_option

    pair_recommendations = await recommend_quizzes_for_study_plan(
        plan.uid,
        u.uid,
        QuizType.PAIR2REL,
    )
    assert {item.quiz.quiz_type for item in pair_recommendations} == {
        QuizType.PAIR2REL,
    }

"""StudyPlanのrepoテスト."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.fixture import (
    create_learning_test_resource,
    fx_learning,
    learning_resource_id,
)
from knowde.integration.quiz.learning.study_plan.domain import StudyPlanDraft
from knowde.integration.quiz.learning.study_plan.repo import (
    create_study_plan,
    fetch_study_plan,
)
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aregister

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_create_and_fetch_study_plan(u: LUser):
    """設定とresourceの優先順を保存して所有者だけが取得."""
    first = await learning_resource_id(u.uid)
    second = await create_learning_test_resource(u.uid)
    draft = StudyPlanDraft(
        name="重点学習",
        resource_ids=[second, first],
        quiz_types=[QuizType.TERM2SENT, QuizType.SENT2TERM],
        n_quiz=3,
        n_option=4,
    )

    created = await create_study_plan(u.uid, draft)

    assert created.name == draft.name
    assert created.resource_ids == draft.resource_ids
    assert created.quiz_types == draft.quiz_types
    assert created.n_quiz == draft.n_quiz
    assert created.n_option == draft.n_option
    assert await fetch_study_plan(created.uid, u.uid) == created

    other = await aregister(email="study-plan-other@ex.com")
    assert await fetch_study_plan(created.uid, other.uid) is None

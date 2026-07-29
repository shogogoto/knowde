"""StudyPlan APIのテスト."""

from httpx import AsyncClient
from starlette import status

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.chain.domain import QuizChain
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.fixture import (
    create_learning_test_resource,
    fx_learning,
    learning_resource_id,
)
from knowde.integration.quiz.learning.progress.domain import (
    ResourceLearningStatus,
)
from knowde.integration.quiz.learning.recommendation.domain import (
    QuizRecommendationReason,
)
from knowde.integration.quiz.learning.study_plan.domain import (
    StudyPlan,
    StudyPlanDraft,
)
from knowde.integration.quiz.learning.study_plan.schema import (
    QuizRecommendationResponse,
)
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aauth_header, aregister

u = async_fixture()(fx_learning)


async def _create_plan_via_api(
    ac: AsyncClient,
    u: LUser,
    draft: StudyPlanDraft,
) -> StudyPlan:
    """APIからStudyPlanを作成."""
    response = await ac.post(
        "/quiz/study-plans",
        json=draft.model_dump(mode="json"),
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_201_CREATED
    return StudyPlan.model_validate(response.json())


@mark_async_test()
async def test_study_plan_crud_api(ac: AsyncClient, u: LUser):
    """StudyPlanをAPIから作成・一覧・取得・更新・削除."""
    first = await learning_resource_id(u.uid)
    second = await create_learning_test_resource(u.uid)
    draft = StudyPlanDraft(
        name="毎日の学習",
        resource_ids=[first, second],
        quiz_types=[QuizType.TERM2SENT, QuizType.SENT2TERM],
        n_quiz=3,
        n_option=3,
    )
    headers = await aauth_header(email=u.email)

    created = await _create_plan_via_api(ac, u, draft)

    response = await ac.get("/quiz/study-plans", headers=headers)
    assert [StudyPlan.model_validate(item) for item in response.json()] == [created]

    response = await ac.get(
        f"/quiz/study-plans/{created.uid}",
        headers=headers,
    )
    assert StudyPlan.model_validate(response.json()) == created

    updated_draft = draft.model_copy(
        update={
            "name": "重点学習",
            "resource_ids": [second, first],
            "n_quiz": 2,
        },
    )
    response = await ac.put(
        f"/quiz/study-plans/{created.uid}",
        json=updated_draft.model_dump(mode="json"),
        headers=headers,
    )
    updated = StudyPlan.model_validate(response.json())
    assert updated.name == updated_draft.name
    assert updated.resource_ids == updated_draft.resource_ids
    assert updated.n_quiz == updated_draft.n_quiz

    response = await ac.delete(
        f"/quiz/study-plans/{created.uid}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await ac.get(
        f"/quiz/study-plans/{created.uid}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@mark_async_test()
async def test_study_plan_recommendation_api(ac: AsyncClient, u: LUser):
    """StudyPlanから推薦を取得し、回答と進捗へ反映."""
    resource_id = await learning_resource_id(u.uid)
    plan = await _create_plan_via_api(
        ac,
        u,
        StudyPlanDraft(
            name="学習",
            resource_ids=[resource_id],
            quiz_types=[QuizType.TERM2SENT],
            n_quiz=1,
            n_option=3,
        ),
    )
    headers = await aauth_header(email=u.email)

    response = await ac.post(
        f"/quiz/study-plans/{plan.uid}/recommendations",
        params={"quiz_type": QuizType.TERM2SENT},
        headers=headers,
    )
    recommendation = QuizRecommendationResponse.model_validate(response.json()[0])
    assert recommendation.resource_id == resource_id
    assert recommendation.quiz_type is QuizType.TERM2SENT
    assert recommendation.reason is QuizRecommendationReason.COVERAGE

    quiz = recommendation.quiz
    response = await ac.post(
        f"/quiz/answer/{quiz.quiz_id}",
        json={"selected": quiz.correct},
        headers=headers,
    )
    chain = QuizChain.model_validate(response.json())
    assert chain.answers[0].is_correct

    response = await ac.get(
        f"/quiz/learning-progress/{resource_id}",
        headers=headers,
    )
    progress = ResourceLearningStatus.model_validate(response.json())
    status = progress.by_quiz_type[QuizType.TERM2SENT]
    assert status.coverage.covered == 1
    assert status.attempt_rate.attempted == 1
    assert status.performance.corrects == 1


@mark_async_test()
async def test_reject_other_users_resource_from_study_plan(
    ac: AsyncClient,
    u: LUser,
):
    """所有していないresourceはStudyPlanへ登録できない."""
    resource_id = await learning_resource_id(u.uid)
    other = await aregister(email="study-plan-api-other@ex.com")
    response = await ac.post(
        "/quiz/study-plans",
        json=StudyPlanDraft(
            name="登録不可",
            resource_ids=[resource_id],
            quiz_types=[QuizType.TERM2SENT],
            n_quiz=1,
            n_option=3,
        ).model_dump(mode="json"),
        headers=await aauth_header(email=other.email),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

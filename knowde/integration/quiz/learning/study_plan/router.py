"""StudyPlan API."""

from uuid import UUID

from fastapi import APIRouter, Response, status

from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.study_plan.domain import (
    StudyPlan,
    StudyPlanDraft,
)
from knowde.integration.quiz.learning.study_plan.schema import (
    QuizRecommendationResponse,
)
from knowde.integration.quiz.learning.study_plan.usecase import (
    create_study_plan,
    delete_study_plan,
    get_study_plan,
    get_study_plans,
    recommend_quizzes_for_study_plan,
    update_study_plan,
)
from knowde.shared.user.router_util import ActiveUser

_router = APIRouter(prefix="/study-plans", tags=["quiz-learning"])


@_router.post("", status_code=status.HTTP_201_CREATED)
async def create_study_plan_api(
    draft: StudyPlanDraft,
    user: ActiveUser,
) -> StudyPlan:
    """StudyPlanを作成."""
    return await create_study_plan(user.uid, draft)


@_router.get("")
async def list_study_plans_api(user: ActiveUser) -> list[StudyPlan]:
    """所有するStudyPlanを一覧取得."""
    return await get_study_plans(user.uid)


@_router.get("/{plan_id}")
async def get_study_plan_api(
    plan_id: UUID,
    user: ActiveUser,
) -> StudyPlan:
    """所有するStudyPlanを取得."""
    return await get_study_plan(plan_id, user.uid)


@_router.put("/{plan_id}")
async def update_study_plan_api(
    plan_id: UUID,
    draft: StudyPlanDraft,
    user: ActiveUser,
) -> StudyPlan:
    """StudyPlan全体を更新."""
    return await update_study_plan(plan_id, user.uid, draft)


@_router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_plan_api(
    plan_id: UUID,
    user: ActiveUser,
) -> Response:
    """StudyPlanを削除."""
    await delete_study_plan(plan_id, user.uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@_router.post("/{plan_id}/recommendations")
async def recommend_study_plan_quizzes_api(
    plan_id: UUID,
    user: ActiveUser,
    quiz_type: QuizType | None = None,
    *,
    generate_missing: bool = True,
) -> list[QuizRecommendationResponse]:
    """StudyPlanの設定で回答可能なクイズを推薦."""
    recommendations = await recommend_quizzes_for_study_plan(
        plan_id,
        user.uid,
        quiz_type,
        generate_missing=generate_missing,
    )
    return [
        QuizRecommendationResponse.from_domain(recommendation)
        for recommendation in recommendations
    ]


def study_plan_router() -> APIRouter:
    """StudyPlan router."""
    return _router

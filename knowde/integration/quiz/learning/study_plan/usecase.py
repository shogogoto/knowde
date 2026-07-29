"""StudyPlanのユースケース."""

from knowde.feature.entry.resource.repo.owner import check_entry_owner
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.recommendation.domain import (
    QuizRecommendation,
)
from knowde.integration.quiz.learning.recommendation.usecase import (
    recommend_quizzes,
)
from knowde.integration.quiz.learning.study_plan.domain import (
    StudyPlan,
    StudyPlanDraft,
)
from knowde.integration.quiz.learning.study_plan.errors import (
    StudyPlanNotFoundError,
    StudyPlanResourceAccessError,
)
from knowde.integration.quiz.learning.study_plan.repo import (
    create_study_plan as create_study_plan_in_repo,
)
from knowde.integration.quiz.learning.study_plan.repo import (
    delete_study_plan as delete_study_plan_in_repo,
)
from knowde.integration.quiz.learning.study_plan.repo import (
    fetch_study_plan,
    list_study_plans,
)
from knowde.integration.quiz.learning.study_plan.repo import (
    update_study_plan as update_study_plan_in_repo,
)
from knowde.shared.types import UUIDy


async def _check_resource_ownership(
    user_id: UUIDy,
    draft: StudyPlanDraft,
) -> None:
    """StudyPlanの全resourceをユーザーが所有しているか確認."""
    for resource_id in draft.resource_ids:
        if not await check_entry_owner(user_id, resource_id):
            msg = f"所有していないresourceはStudyPlanへ登録できません: {resource_id}"
            raise StudyPlanResourceAccessError(msg=msg)


async def create_study_plan(
    user_id: UUIDy,
    draft: StudyPlanDraft,
) -> StudyPlan:
    """所有resourceからStudyPlanを作成."""
    await _check_resource_ownership(user_id, draft)
    return await create_study_plan_in_repo(user_id, draft)


async def get_study_plan(
    plan_id: UUIDy,
    user_id: UUIDy,
) -> StudyPlan:
    """所有するStudyPlanを取得."""
    plan = await fetch_study_plan(plan_id, user_id)
    if plan is None:
        msg = f"StudyPlanが見つかりません: {plan_id}"
        raise StudyPlanNotFoundError(msg=msg)
    return plan


async def get_study_plans(user_id: UUIDy) -> list[StudyPlan]:
    """所有するStudyPlanを一覧取得."""
    return await list_study_plans(user_id)


async def update_study_plan(
    plan_id: UUIDy,
    user_id: UUIDy,
    draft: StudyPlanDraft,
) -> StudyPlan:
    """所有するStudyPlanを更新."""
    await _check_resource_ownership(user_id, draft)
    plan = await update_study_plan_in_repo(plan_id, user_id, draft)
    if plan is None:
        msg = f"StudyPlanが見つかりません: {plan_id}"
        raise StudyPlanNotFoundError(msg=msg)
    return plan


async def delete_study_plan(
    plan_id: UUIDy,
    user_id: UUIDy,
) -> None:
    """所有するStudyPlanを削除."""
    if not await delete_study_plan_in_repo(plan_id, user_id):
        msg = f"StudyPlanが見つかりません: {plan_id}"
        raise StudyPlanNotFoundError(msg=msg)


async def recommend_quizzes_for_study_plan(
    plan_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType | None = None,
) -> list[QuizRecommendation]:
    """保存されたStudyPlanの設定でクイズを推薦."""
    plan = await get_study_plan(plan_id, user_id)

    # 過去に保存された少ない出題数でも、選択した各形式を最低1問は試す。
    n_quiz = max(plan.n_quiz, len(plan.quiz_types))
    quotient, remainder = divmod(n_quiz, len(plan.quiz_types))
    quiz_types = (
        [quiz_type]
        if quiz_type is not None and quiz_type in plan.quiz_types
        else plan.quiz_types
        if quiz_type is None
        else []
    )
    pools = []
    for current_quiz_type in quiz_types:
        index = plan.quiz_types.index(current_quiz_type)
        count = quotient + (index < remainder)
        pools.append(
            await recommend_quizzes(
                plan.resource_ids,
                user_id,
                current_quiz_type,
                CandidateType.ALL,
                count,
                plan.n_option,
            ),
        )

    longest = max((len(pool) for pool in pools), default=0)
    return [
        pool[index] for index in range(longest) for pool in pools if index < len(pool)
    ]

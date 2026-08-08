"""StudyPlanから理解の確認と復習へ進む、代表的な学習シナリオ.

利用者から見た流れ:

1. StudyPlanで「どのresourceを、どのQuizTypeで学ぶか」を決める。
2. Recommendationから、今回答するQuizを受け取る。
3. Quizへ回答し、Answerを含むQuizChainを受け取る。
4. Chain上のSentenceを選び、その周辺のQuizを1ホップだけ展開する。
5. LearningProgressで、用意・回答・正解が記録されたことを確認する。

各段階は独立した操作である。frontendは利用者の選択を挟みながら、
これらのAPIを順に呼ぶ。
"""

from uuid import UUID

from httpx import AsyncClient
from starlette import status

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.quiz.chain.domain import QuizChain
from knowde.feature.quiz.domain.parts import QuizType
from knowde.feature.quiz.learning.fixture import (
    fx_learning,
    learning_resource_id,
)
from knowde.feature.quiz.learning.progress.domain import (
    ResourceLearningStatus,
)
from knowde.feature.quiz.learning.study_plan.domain import (
    StudyPlan,
    StudyPlanDraft,
)
from knowde.feature.quiz.learning.study_plan.schema import (
    QuizRecommendationResponse,
)
from knowde.feature.user.label import LUser
from knowde.feature.user.testing import aauth_header

u = async_fixture()(fx_learning)


async def _create_daily_plan(
    ac: AsyncClient,
    u: LUser,
    resource_id: UUID,
) -> StudyPlan:
    """学習対象と出題方法を保存する."""
    response = await ac.post(
        "/quiz/study-plans",
        json=StudyPlanDraft(
            name="毎日の学習",
            resource_ids=[resource_id],
            quiz_types=[QuizType.TERM2SENT],
            n_quiz=1,
            n_option=3,
        ).model_dump(mode="json"),
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_201_CREATED
    return StudyPlan.model_validate(response.json())


async def _recommend_next_quiz(
    ac: AsyncClient,
    u: LUser,
    plan: StudyPlan,
) -> QuizRecommendationResponse:
    """StudyPlanに従って、次に回答するQuizを得る."""
    response = await ac.post(
        f"/quiz/study-plans/{plan.uid}/recommendations",
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_200_OK
    return QuizRecommendationResponse.model_validate(response.json()[0])


async def _answer_correctly(
    ac: AsyncClient,
    u: LUser,
    recommendation: QuizRecommendationResponse,
) -> QuizChain:
    """回答し、結果と復習材料をひとつのChainとして得る."""
    quiz = recommendation.quiz
    response = await ac.post(
        f"/quiz/answer/{quiz.quiz_id}",
        json={"selected": quiz.correct},
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_200_OK
    return QuizChain.model_validate(response.json())


async def _expand_selected_sentence(
    ac: AsyncClient,
    u: LUser,
    chain: QuizChain,
) -> QuizChain:
    """回答で選んだSentenceから、関係するQuizを1ホップ展開する."""
    selected = chain.answers[0].selected[0]
    response = await ac.get(
        f"/quiz/chain/sentences/{selected}",
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_200_OK
    return QuizChain.model_validate(response.json())


async def _fetch_progress(
    ac: AsyncClient,
    u: LUser,
    resource_id: UUID,
) -> ResourceLearningStatus:
    """resourceをどこまで学習したか確認する."""
    response = await ac.get(
        f"/quiz/learning-progress/{resource_id}",
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_200_OK
    return ResourceLearningStatus.model_validate(response.json())


@mark_async_test()
async def test_learning_journey_from_plan_to_review(
    ac: AsyncClient,
    u: LUser,
):
    """学習対象を決め、回答し、周辺を復習して、進捗を確認する."""
    resource_id = await learning_resource_id(u.uid)

    plan = await _create_daily_plan(ac, u, resource_id)
    recommendation = await _recommend_next_quiz(ac, u, plan)

    assert recommendation.resource_id == resource_id

    answered = await _answer_correctly(ac, u, recommendation)

    assert answered.answers[0].is_correct
    assert answered.answers[0].quiz_uid == recommendation.quiz.quiz_id
    assert answered.sentences
    assert answered.links

    reviewed = await _expand_selected_sentence(ac, u, answered)

    assert [quiz.quiz_id for quiz in reviewed.quizzes] == [
        recommendation.quiz.quiz_id,
    ]
    assert len(reviewed.sentences) == 1  # 自動で連鎖せず、常に1ホップで止まる

    progress = await _fetch_progress(ac, u, resource_id)
    term_to_sentence = progress.by_quiz_type[QuizType.TERM2SENT]

    assert term_to_sentence.coverage.covered == 1  # Quizを用意できた
    assert term_to_sentence.attempt_rate.attempted == 1  # 回答した
    assert term_to_sentence.performance.corrects == 1  # 正解した

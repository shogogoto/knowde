"""StudyPlanのrepo."""

from datetime import datetime
from uuid import uuid4

from neomodel import adb

from knowde.feature.primitive.types import UUIDy, to_uuid
from knowde.feature.primitive.util import TZ, neo4j_dt_validator
from knowde.feature.quiz.domain.parts import QuizType
from knowde.feature.quiz.learning.study_plan.domain import (
    StudyPlan,
    StudyPlanDraft,
)
from knowde.feature.quiz.learning.study_plan.errors import (
    StudyPlanCreateError,
)


async def fetch_study_plan(
    plan_id: UUIDy,
    user_id: UUIDy,
) -> StudyPlan | None:
    """所有者に紐づくStudyPlanを取得."""
    q = """
        MATCH (plan: StudyPlan {uid: $plan_id})
            -[:OWNED]->(:User {uid: $user_id})
        MATCH (plan)-[study:STUDY]->(resource: Resource)
        WITH plan, study, resource
        ORDER BY study.position ASC
        RETURN
            plan.uid,
            plan.name,
            plan.quiz_types,
            plan.n_quiz,
            plan.n_option,
            plan.created,
            COLLECT(resource.uid)
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "plan_id": to_uuid(plan_id).hex,
            "user_id": to_uuid(user_id).hex,
        },
    )
    if not rows:
        return None

    uid, name, quiz_types, n_quiz, n_option, created, resource_ids = rows[0]
    return StudyPlan(
        uid=uid,
        name=name,
        resource_ids=resource_ids,
        quiz_types=[QuizType[quiz_type] for quiz_type in quiz_types],
        n_quiz=n_quiz,
        n_option=n_option,
        created=neo4j_dt_validator(created),
    )


async def list_study_plans(user_id: UUIDy) -> list[StudyPlan]:
    """ユーザーが所有するStudyPlanを新しい順に取得."""
    q = """
        MATCH (plan: StudyPlan)-[:OWNED]->(:User {uid: $user_id})
        RETURN plan.uid
        ORDER BY plan.created DESC, plan.uid ASC
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"user_id": to_uuid(user_id).hex},
    )
    plans = []
    for row in rows:
        plan = await fetch_study_plan(row[0], user_id)
        if plan is not None:
            plans.append(plan)
    return plans


async def create_study_plan(
    user_id: UUIDy,
    draft: StudyPlanDraft,
) -> StudyPlan:
    """StudyPlanと対象resourceを永続化."""
    plan_id = uuid4()
    now = datetime.now(tz=TZ)
    resource_ids = list(dict.fromkeys(draft.resource_ids))
    q = """
        MATCH (user: User {uid: $user_id})
        MATCH (resource: Resource)
        WHERE resource.uid IN $resource_ids
        WITH user, COLLECT(DISTINCT resource) AS resources
        WHERE size(resources) = size($resource_ids)
        CREATE (plan: StudyPlan {
            uid: $plan_id,
            name: $name,
            quiz_types: $quiz_types,
            n_quiz: $n_quiz,
            n_option: $n_option,
            created: datetime($now)
        })-[:OWNED]->(user)
        WITH plan
        UNWIND range(0, size($resource_ids) - 1) AS position
        MATCH (resource: Resource {uid: $resource_ids[position]})
        CREATE (plan)-[:STUDY {position: position}]->(resource)
        RETURN DISTINCT plan.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "plan_id": plan_id.hex,
            "user_id": to_uuid(user_id).hex,
            "resource_ids": [uid.hex for uid in resource_ids],
            "name": draft.name,
            "quiz_types": [quiz_type.name for quiz_type in draft.quiz_types],
            "n_quiz": draft.n_quiz,
            "n_option": draft.n_option,
            "now": now.isoformat(),
        },
    )
    if not rows:
        msg = "ユーザーまたは対象resourceが存在せずStudyPlanを作成できません"
        raise StudyPlanCreateError(msg)

    plan = await fetch_study_plan(plan_id, user_id)
    if plan is None:
        msg = "作成したStudyPlanを復元できません"
        raise StudyPlanCreateError(msg)
    return plan


async def update_study_plan(
    plan_id: UUIDy,
    user_id: UUIDy,
    draft: StudyPlanDraft,
) -> StudyPlan | None:
    """所有するStudyPlanの設定と対象resourceを置き換える."""
    resource_ids = list(dict.fromkeys(draft.resource_ids))
    q = """
        MATCH (plan: StudyPlan {uid: $plan_id})
            -[:OWNED]->(:User {uid: $user_id})
        MATCH (resource: Resource)
        WHERE resource.uid IN $resource_ids
        WITH plan, COLLECT(DISTINCT resource) AS resources
        WHERE size(resources) = size($resource_ids)
        SET
            plan.name = $name,
            plan.quiz_types = $quiz_types,
            plan.n_quiz = $n_quiz,
            plan.n_option = $n_option
        WITH plan
        OPTIONAL MATCH (plan)-[old:STUDY]->()
        DELETE old
        WITH DISTINCT plan
        UNWIND range(0, size($resource_ids) - 1) AS position
        MATCH (resource: Resource {uid: $resource_ids[position]})
        CREATE (plan)-[:STUDY {position: position}]->(resource)
        RETURN DISTINCT plan.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "plan_id": to_uuid(plan_id).hex,
            "user_id": to_uuid(user_id).hex,
            "resource_ids": [uid.hex for uid in resource_ids],
            "name": draft.name,
            "quiz_types": [quiz_type.name for quiz_type in draft.quiz_types],
            "n_quiz": draft.n_quiz,
            "n_option": draft.n_option,
        },
    )
    if not rows:
        return None
    return await fetch_study_plan(plan_id, user_id)


async def delete_study_plan(
    plan_id: UUIDy,
    user_id: UUIDy,
) -> bool:
    """所有するStudyPlanを削除."""
    q = """
        MATCH (plan: StudyPlan {uid: $plan_id})
            -[:OWNED]->(:User {uid: $user_id})
        DETACH DELETE plan
        RETURN count(*) AS deleted
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "plan_id": to_uuid(plan_id).hex,
            "user_id": to_uuid(user_id).hex,
        },
    )
    return bool(rows and rows[0][0])

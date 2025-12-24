"""quiz repo."""

import random
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from neomodel import adb
from pydantic import Field, TypeAdapter

from knowde.integration.quiz.domain.domain import (
    QuizType,
)
from knowde.integration.quiz.repo.select_option.distract import (
    list_candidates_by_radius,
)
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.util import TZ

type NOption = Annotated[int, Field(gt=2, title="選択肢の数")]
nopt_adapter = TypeAdapter(NOption)


# 誤答肢選択戦略
async def create_term2sent_quiz(
    target_sent_uid: UUIDy,
    radius: int | None = None,
    n_option: int = 4,  # 選択肢の数
    now: datetime | None = None,
    quiz_uid: UUID | None = None,
) -> UUID:
    """単文当てクイズの永続化."""
    if now is None:
        now = datetime.now(tz=TZ)
    if quiz_uid is None:
        quiz_uid = uuid4()
    q = """
        MATCH (tgt: Sentence {uid: $target_uid})
        CREATE (quiz: Quiz {
            uid: $quiz_uid
            , statement_type: $statement_type
            , is_link_broken: false
            , created: datetime($now)
        })-[:QUIZ_TARGET]->(tgt)
        WITH quiz
        UNWIND $dist_uids AS duid
        MATCH (dst: Sentence {uid: duid})
        CREATE (quiz)-[:QUIZ_OPTION]->(dst)
        RETURN quiz
            , COLLECt(dst) AS distractors
    """
    n_sample = nopt_adapter.validate_python(n_option) - 1  # target分を引く
    uids = await list_candidates_by_radius(target_sent_uid, radius)
    opt_uids = [to_uuid(uid) for uid in random.sample(uids, n_sample)]
    _rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_uid": quiz_uid.hex,
            "target_uid": to_uuid(target_sent_uid).hex,
            "dist_uids": [u.hex for u in opt_uids],
            "statement_type": QuizType.TERM2SENT.name,
            "now": now.isoformat(),
        },
    )
    return quiz_uid


async def create_sent2term_quiz(
    target_sent_uid: UUIDy,
    radius: int | None = None,
    n_option: int = 4,  # 選択肢の数
    now: datetime | None = None,
) -> UUID:
    """用語当てクイズの永続化."""

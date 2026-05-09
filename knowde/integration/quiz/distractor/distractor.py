"""repo."""

from uuid import UUID

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.domain import sample_safe
from knowde.shared.types import UUIDy

"""
誤答肢の撮り方はQuizTypeに依存


"""


async def fetch_distractor_ids(
    sent_id: UUIDy,
    ct: CandidateType,
    limit: int,
    must_has_term: bool,  # noqa: FBT001
) -> list[UUID]:
    """誤答肢を取得する."""
    cand_uids = await ct.fetch(
        sent_id,
        must_has_term=must_has_term,
    )
    uids = [u for u in cand_uids if u != sent_id]
    return sample_safe(uids, n_option=limit)

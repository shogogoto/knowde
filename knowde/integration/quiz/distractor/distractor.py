"""repo."""

from uuid import UUID

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.domain import ramdom_sample_safe
from knowde.shared.types import UUIDy


async def fetch_distractor_ids(
    sent_ids: list[UUIDy],
    ct: CandidateType,
    limit: int,
    must_has_term: bool,  # noqa: FBT001
) -> list[UUID]:
    """誤答肢を取得する."""
    cand_uids = await ct.fetch(
        sent_ids,
        must_has_term=must_has_term,
    )
    exclude = set(sent_ids)
    uids = [u for u in cand_uids if u not in exclude]
    return ramdom_sample_safe(uids, n_sample=limit)

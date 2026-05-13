"""repo."""

from uuid import UUID

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.domain import random_sample_safe
from knowde.integration.quiz.errors import InsufficientOptionsError
from knowde.shared.types import UUIDy


async def fetch_distractor_ids(
    sent_ids: list[UUIDy],
    ct: CandidateType,
    n_distractor: int,
    must_has_term: bool,  # noqa: FBT001
) -> list[UUID]:
    """誤答肢を取得する."""
    cand_uids = await ct.fetch(
        sent_ids,
        must_has_term=must_has_term,
    )
    exclude = set(sent_ids)
    uids = [u for u in cand_uids if u not in exclude]
    retval = random_sample_safe(uids, n_sample=n_distractor)
    actual = len(retval)
    if actual != n_distractor:
        msg = f"誤答肢が指定数{n_distractor}と一致しない: {actual}"
        raise InsufficientOptionsError(msg)
    return retval

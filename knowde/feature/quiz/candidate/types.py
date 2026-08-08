"""候補出しタイプ."""

from enum import StrEnum, auto
from uuid import UUID

from knowde.feature.domain.types import UUIDy
from knowde.feature.quiz.candidate.candidate import (
    fetch_sent2resource_id,
    list_candidates_by_radius,
    list_candidates_in_resource,
    list_top_scoring_candidates,
)


class CandidateType(StrEnum):
    """候補出しタイプ."""

    # 半径
    NEAR = auto()
    MID = auto()
    FAR = auto()
    ALL = auto()  # 全体が候補

    # スコア上位指定
    TOP_ELITE = auto()
    TOP_NORMAL = auto()
    TOP_WIDE = auto()

    @property
    def _limit(self) -> int:
        """候補出し用パラメータを返す."""
        if self == CandidateType.ALL:
            raise ValueError

        return {
            CandidateType.NEAR: 2,
            CandidateType.MID: 4,
            CandidateType.FAR: 6,
            CandidateType.TOP_ELITE: 20,
            CandidateType.TOP_NORMAL: 50,
            CandidateType.TOP_WIDE: 80,
        }[self]

    @property
    def is_radius_type(self) -> bool:
        """半径探索か否か."""
        return self in {CandidateType.NEAR, CandidateType.MID, CandidateType.FAR}

    @property
    def is_top_type(self) -> bool:
        """スコア上位指定か否か."""
        return self in {
            CandidateType.TOP_ELITE,
            CandidateType.TOP_NORMAL,
            CandidateType.TOP_WIDE,
        }

    async def fetch(
        self,
        target_sent_ids: list[UUIDy],
        must_has_term: bool = False,  # noqa: FBT001, FBT002
        exclude_sent_ids: list[UUIDy] | None = None,
    ) -> list[UUID]:
        """候補ID一覧を返す."""
        if exclude_sent_ids is None:
            exclude_sent_ids = []
        if self == CandidateType.ALL:
            return await list_candidates_in_resource(
                target_sent_ids,
                only_with_term=must_has_term,
                exclude_sent_ids=exclude_sent_ids,
            )
        if self.is_radius_type:
            return await list_candidates_by_radius(
                target_sent_ids,
                radius=self._limit,
                only_with_term=must_has_term,
                exclude_sent_ids=exclude_sent_ids,
            )

        ruids = await fetch_sent2resource_id(target_sent_ids)
        return await list_top_scoring_candidates(
            ruids,
            only_with_term=must_has_term,
            exclude_sent_ids=target_sent_ids + exclude_sent_ids,
        )

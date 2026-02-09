"""候補出しタイプ."""

from enum import StrEnum, auto


class CandidateType(StrEnum):
    """候補出しタイプ."""

    # 半径
    NEAR = auto()
    MID = auto()
    FAR = auto()
    WHOLE = auto()  # 全体が候補

    # スコア上位指定
    TOP_ELITE = auto()
    TOP_NORMAL = auto()
    TOP_WIDE = auto()

    @property
    def config(self) -> dict:
        """候補出し用パラメータを返す."""
        return {
            CandidateType.NEAR:       {"radius": 2},
            CandidateType.MID:        {"radius": 4},
            CandidateType.FAR:        {"radius": 6},
            CandidateType.WHOLE:      {"radius": None},
            CandidateType.TOP_ELITE:  {"n_candidate": 5},
            CandidateType.TOP_NORMAL: {"n_candidate": 10},
            CandidateType.TOP_WIDE:   {"n_candidate": 30},
        }[self]  # fmt: skip

    def is_radius_type(self) -> bool:
        """半径探索か否か."""
        return self in {CandidateType.NEAR, CandidateType.MID, CandidateType.FAR}

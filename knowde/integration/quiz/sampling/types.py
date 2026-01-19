"""選択肢選定ロジック."""

from enum import StrEnum, auto


class SamplingType(StrEnum):
    """選択肢選定ロジックの種類."""

    RANDOM = auto()
    CLOSER = auto()  # 近いものか順に選ぶ
    TOP_SCORE = auto()


async def sample_by_type(t: SamplingType, n_option: int):  # noqa: RUF029
    """選択肢選定ロジックから選択肢を取得."""
    match t:
        case SamplingType.RANDOM:
            pass
        case SamplingType.CLOSER:
            pass
        case SamplingType.TOP_SCORE:
            pass


async def select_by_radius():
    """半径探索."""

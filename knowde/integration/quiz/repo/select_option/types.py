"""選択肢選定ロジック."""

from enum import StrEnum, auto


class SelectOptionType(StrEnum):
    """選択肢選定ロジックの種類."""

    # radiusは自動調整されるから指定しなくてよい
    # 候補数の指定は共通しているので、それは引数として渡す
    RADIUS_RANDOM = auto()
    RESOURCE_RANDOM = auto()
    TOP_SCORE = auto()


def select_by_option_type(t: SelectOptionType, n_option: int):
    """選択肢選定ロジックから選択肢を取得."""
    match t:
        case SelectOptionType.RADIUS_RANDOM:
            pass
        case SelectOptionType.RESOURCE_RANDOM:
            pass
        case SelectOptionType.TOP_SCORE:
            pass


async def select_by_radius():
    """半径探索."""

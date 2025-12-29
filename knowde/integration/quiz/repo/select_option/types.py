"""選択肢選定ロジック."""

from enum import StrEnum, auto


class SelectOptionType(StrEnum):
    """選択肢選定ロジックの種類."""

    # radiusは自動調整されるから指定しなくてよい
    # 候補数の指定も欲しいかも
    RADIUS_RANDOM_4 = auto()
    RESOURCE_RANDOM_4 = auto()
    TOP_SCORE = auto()

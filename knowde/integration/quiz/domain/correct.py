"""正答の与え方の戦略."""

from collections.abc import Callable

from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizRel

type CorrectStrategy = Callable[[str], bool]


def correct_is_target(src: QuizSource) -> CorrectStrategy:
    """クイズ対象を正答とする."""

    def _f(uid: str) -> bool:
        return uid == src.target_id

    return _f


def correct_is_specific_rels(src: QuizSource, rels: list[QuizRel]) -> CorrectStrategy:
    """特定の関係を正答とする."""

    def _f(uid: str) -> bool:
        return src.get(uid).rels == rels and uid != src.target_id

    return _f

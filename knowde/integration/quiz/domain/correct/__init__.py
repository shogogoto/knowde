"""正答の指定ロジック."""

from collections.abc import Callable

from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizRel

type CorrectStrategy = Callable[[str], bool]


def correct_target(src: QuizSource) -> CorrectStrategy:
    """クイズ対象を正答とする."""

    def _f(uid: str) -> bool:
        return uid == src.target_id

    return _f


def correct_specific_rels(src: QuizSource, rels: list[QuizRel]) -> CorrectStrategy:
    """特定の関係を正答とする."""

    def _f(uid: str) -> bool:
        return src.get_by_id(uid).rels == rels and uid != src.target_id

    return _f


def correct_rels_by_id(src: QuizSource, id_: str) -> CorrectStrategy:
    """対象と指定間の関係を正答とする."""

    def _f(uid: str) -> bool:
        return (
            src.get_by_id(uid).rels == src.get_by_id(id_).rels and uid != src.target_id
        )

    return _f

"""quiz repo."""

from knowde.feature.domain.types import UUIDy


class DistractStrategy:
    """誤答肢の生成方法."""


def create_term_quiz(sent_uid: UUIDy):
    """指定単文の用語を選ぶクイズを作成する."""

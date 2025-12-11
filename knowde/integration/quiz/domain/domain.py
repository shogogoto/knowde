"""quiz domain."""

from enum import StrEnum

from pydantic import BaseModel

from knowde.feature.parsing.primitive.mark import inject2placeholder

QUIZ_PLACEHOLDER = "$@"


class QuizStatement(StrEnum):
    """問題文の種類."""

    SENT2TERM = "$@に合う用語を当ててください"
    TERM2SENT = "$@に合う単文を当ててください"

    # 提示したEdgeTypeと関連する単文を答えさせる
    REL2SENT = "関係$@で繋がる単文を当ててください"
    # 提示した単文と対象間のEdgeTypeを答えさせる
    SENT2REL = "$@から$@への関係を当ててください"
    PATH = "$@の経路を当ててください"

    def inject(self, vals: list[str]) -> str:
        """プレースホルダーを置き換えて返す."""
        return inject2placeholder(str(self), vals, QUIZ_PLACEHOLDER)


# 複数選択がマルになるケースにも対応する

# class QuizScope(BaseModel,)


class DistractorStrategy(BaseModel):
    """誤答肢選択."""

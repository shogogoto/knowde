"""構成要素となる部品."""

from collections.abc import Hashable
from enum import StrEnum

from pydantic import BaseModel

from knowde.feature.parsing.primitive.mark import inject2placeholder
from knowde.feature.parsing.sysnet.sysnode import Def

QUIZ_PLACEHOLDER = "$@"


class QuizStatementType(StrEnum):
    """問題文の種類."""

    SENT2TERM = "$@に合う用語を当ててください"
    TERM2SENT = "$@に合う文を当ててください"

    # 提示したEdgeTypeと関連する単文 or 定義を答えさせる
    EDGE2SENT = "$@と$@関係で繋がる単文を当ててください"
    # 提示した単文と対象間のEdgeTypeを答えさせる
    SENT2EDGE = "$@から$@への関係を当ててください"
    PATH = "$@の経路を当ててください"

    def inject(self, vals: list[str]) -> str:
        """プレースホルダーを置き換えて返す."""
        return inject2placeholder(
            str(self),
            vals,
            QUIZ_PLACEHOLDER,
            surround_pre="'",
            surround_post="'",
        )


# EdgeTypeとの重複あり
#   問題文への表示を司る
class QuizRel(StrEnum):
    """クイズ対象との関係."""

    PARENT = "親"
    DETAIL = "詳細"  # belowとその兄弟
    PREMISE = "前提"
    CONCLUSION = "結論"
    # 分かりにくい表現
    REF_BY = "用語被参照"
    REF = "用語参照"
    GENERAL = "一般"
    EXAMPLE = "具体例"


class QuizOption(BaseModel, frozen=True):
    """クイズ選択肢."""

    val: str | Def | Hashable
    rel: QuizRel | None = None

    @classmethod
    def create(  # noqa: D102
        cls,
        sentence: str,
        names: list[str] | None = None,
        rel: QuizRel | None = None,
    ):
        val = Def.create(sentence, names=names)
        return cls(val=val, rel=rel)

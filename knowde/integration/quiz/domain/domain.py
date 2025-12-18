"""quiz domain."""

from enum import Enum, StrEnum
from textwrap import indent

from pydantic import BaseModel, Field

from knowde.feature.parsing.primitive.mark import inject2placeholder
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.integration.quiz.errors import AnswerError, QuizOptionsMustBeDefError

QUIZ_PLACEHOLDER = "$@"


class QuizStatementType(StrEnum):
    """問題文の種類."""

    SENT2TERM = "$@に合う用語を当ててください"
    TERM2SENT = "$@に合う単文を当ててください"

    # 提示したEdgeTypeと関連する単文 or 定義を答えさせる
    EDGE2SENT = "$@と関係$@で繋がる単文を当ててください"
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
class QuizTargetRel(StrEnum):
    """クイズ対象との関係."""

    PARENT = "親"
    DETAIL = "詳細"  # belowとその兄弟
    PREMISE = "前提"
    CONCLUSION = "結論"
    # 分かりにくい表現
    REFERRED = "用語被参照"
    REFEER = "用語参照"
    ABSTRACT = "抽象"
    EXAMPLE = "具体"


class QuizOption(BaseModel, frozen=True):
    """クイズ選択肢."""

    val: str | Def
    rel: QuizTargetRel | None = None

    @classmethod
    def create(  # noqa: D102
        cls,
        sentence: str,
        names: list[str] | None = None,
        rel: QuizTargetRel | None = None,
    ):
        val = Def.create(sentence, names=names)
        return cls(val=val, rel=rel)


# 便利なgetterを備えるのみ
class QuizSource(BaseModel, frozen=True):
    """クイズ生成のための情報源."""

    statement_type: QuizStatementType
    # テストしやすいので UUIDではなくstrへ
    target_id: str
    optins: dict[str, QuizOption]

    @property
    def tgt(self) -> QuizOption:  # noqa: D102
        return self.optins[self.target_id]

    @property
    def tgt_def(self) -> Def:
        """クイズ対象."""
        tgt = self.optins[self.target_id].val
        if isinstance(tgt, Def):
            return tgt
        msg = "クイズ対象が用語を持たない"
        raise QuizOptionsMustBeDefError(msg)

    @property
    def tgt_sent(self) -> str:
        """クイズ対象の単文."""
        tgt = self.optins[self.target_id].val
        if isinstance(tgt, Def):
            return str(tgt.sentence)
        return tgt

    @property
    def distractor_defs(self) -> dict[str, Def]:
        """誤答肢の定義."""
        dists = {k: v.val for k, v in self.optins.items() if k != self.target_id}
        defs = {k: v for k, v in dists.items() if isinstance(v, Def)}
        if len(defs) != len(dists):
            msg = "誤答肢に用語なし単文が含まれている"
            raise QuizOptionsMustBeDefError(msg)
        return defs


class Quiz(BaseModel, frozen=True):
    """読める状態の問題文と選択肢を備えたクイズ."""

    uid: str = Field(title="クイズID")
    # 既に読める状態の問題文や選択肢
    statement: str = Field(title="問題文")
    options: dict[str, str] = Field(title="選択肢")
    correct: list[str] = Field(title="正解")

    @property
    def string(self) -> str:
        """問題文."""
        s = f"{self.statement}\n"
        ops = [indent(op, "  * ") for op in self.options.values()]
        s += "\n".join(ops)
        return s

    def answer(self, selected: list[str]) -> "Answer":
        """適切な選択肢を回答する."""
        for s in selected:
            if s not in self.options:
                msg = f"選択肢に存在しない回答; {s} not in {list(self.options.keys())}"
                raise AnswerError(msg)

        return Answer(selected=selected, quiz=self)


# TODO:  何も答えないのが正解、というパターンも欲しい  # noqa: FIX002, TD002, TD003
class Answer(BaseModel, frozen=True):
    """回答."""

    # answer_uid: str
    selected: list[str]  # 複数選択可
    quiz: Quiz

    def is_corrent(self) -> bool:
        """正解かどうか."""
        selected = set(self.selected)
        correct = set(self.quiz.correct)
        return selected == correct


class QuizRel(Enum):
    """関係クイズ用の."""

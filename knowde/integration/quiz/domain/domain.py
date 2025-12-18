"""quiz domain."""

from textwrap import indent

from pydantic import BaseModel, Field

from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.integration.quiz.errors import AnswerError, QuizOptionsMustBeDefError

from .parts import QuizOption, QuizStatementType


class QuizSource(BaseModel, frozen=True):
    """クイズ生成のための情報源.

    便利なgetterを備えるのみ
    """

    statement_type: QuizStatementType
    target_id: str  # テストしやすいので UUIDではなくstrへ
    # targetが答えになるとは限らない
    sources: dict[str, QuizOption] = Field(title="クイズの元となるメンバ")

    @property
    def tgt(self) -> QuizOption:  # noqa: D102
        return self.sources[self.target_id]

    @property
    def tgt_def(self) -> Def:
        """クイズ対象."""
        tgt = self.sources[self.target_id].val
        if isinstance(tgt, Def):
            return tgt
        msg = "クイズ対象が用語を持たない"
        raise QuizOptionsMustBeDefError(msg)

    @property
    def tgt_sent(self) -> str:
        """クイズ対象の単文."""
        tgt = self.sources[self.target_id].val
        if isinstance(tgt, Def):
            return str(tgt.sentence)
        return str(tgt)

    @property
    def distractors(self) -> dict[str, QuizOption]:
        """誤答肢."""
        return {k: v for k, v in self.sources.items() if k != self.target_id}

    @property
    def distractor_defs(self) -> dict[str, Def]:
        """誤答肢の定義."""
        dists = {k: v.val for k, v in self.distractors.items()}
        defs = {k: v for k, v in dists.items() if isinstance(v, Def)}
        if len(defs) != len(dists):
            msg = "誤答肢に用語なし単文が含まれている"
            raise QuizOptionsMustBeDefError(msg)
        return defs

    def sentence_options(self) -> dict[str, str]:
        """文字列化した選択肢."""
        return {
            self.target_id: str(self.tgt_sent),
            **{k: str(v.sentence) for k, v in self.distractor_defs.items()},
        }

    def term_options(self) -> dict[str, str]:
        """文字列化した選択肢."""
        return {
            **{k: str(v.val) for k, v in self.sources.items()},
        }


class ReadableQuiz(BaseModel, frozen=True):
    """「読める状態」の問題文と選択肢を備えたクイズ."""

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
    quiz: ReadableQuiz

    def is_corrent(self) -> bool:
        """正解かどうか."""
        selected = set(self.selected)
        correct = set(self.quiz.correct)
        return selected == correct

"""quiz domain."""

from collections.abc import Iterable
from textwrap import indent

from more_itertools import duplicates_everseen, flatten
from pydantic import BaseModel, Field, model_validator

from knowde.feature.knowde import Knowde
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.integration.quiz.errors import (
    AnswerError,
    QuizDuplicateError,
    QuizOptionsMustBeDefError,
)
from knowde.shared.types import NXGraph

from .parts import QuizOption, QuizStatementType


class QuizSourceContainer(BaseModel, frozen=True):
    """quiz source用id容れ."""

    quiz_id: str
    statement_type: QuizStatementType  # build方法を指定してくれる
    target_id: str
    source_ids: set[str]
    g: NXGraph  # EdgeType-QuizRel用

    @staticmethod
    def concat_uids_for_batch_fetch(
        cases: Iterable["QuizSourceContainer"],
    ) -> Iterable[str]:
        """一括詳細取得用にuidをまとめる."""
        # 都度 fetchしてたら通信が無駄に増えて遅い
        return set(flatten([[c.target_id, *c.source_ids] for c in cases]))

    def to_source(self, uid2kn: dict[str, Knowde]) -> "QuizSource":
        """変換."""
        return QuizSource(
            statement_type=self.statement_type,
            target_id=self.target_id,
            target=QuizOption(val=uid2kn[self.target_id].to_str_or_def()),
            sources={
                uid: QuizOption(val=uid2kn[uid].to_str_or_def())
                for uid in self.source_ids
            },
        )


class QuizSource(BaseModel, frozen=True):
    """クイズ生成のための情報源.

    便利なgetterを備えるのみ
    """

    statement_type: QuizStatementType  # build方法を指定してくれる
    target_id: str  # テストしやすいので UUIDではなくstrへ
    target: QuizOption
    # targetが答えになるとは限らない
    sources: dict[str, QuizOption] = Field(title="クイズの元となるメンバ")

    @model_validator(mode="after")
    def option_duplicate_check(self):
        """重複チェック."""
        options = [self.target, *list(self.sources.values())]
        dups = list(duplicates_everseen(options))
        if len(dups) > 0:
            msg = f"同一のクイズ選択肢が指定されています: {dups}"
            raise QuizDuplicateError(msg)
        return self

    @property
    def tgt_def(self) -> Def:
        """クイズ対象."""
        tgt = self.target.val
        if isinstance(tgt, Def):
            return tgt
        msg = "クイズ対象が用語を持たない"
        raise QuizOptionsMustBeDefError(msg)

    @property
    def tgt_sent(self) -> str:
        """クイズ対象の単文."""
        tgt = self.target.val
        if isinstance(tgt, Def):
            return str(tgt.sentence)
        return str(tgt)

    @property
    def source_defs(self) -> dict[str, Def]:
        """誤答肢の定義."""
        dists = {k: v.val for k, v in self.sources.items()}
        defs = {k: v for k, v in dists.items() if isinstance(v, Def)}
        if len(defs) != len(dists):
            msg = "誤答肢に用語なし単文が含まれている"
            raise QuizOptionsMustBeDefError(msg)
        return defs


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

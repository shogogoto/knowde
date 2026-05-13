"""quiz domain."""

from textwrap import indent
from uuid import UUID

from more_itertools import duplicates_everseen
from pydantic import BaseModel, Field, model_validator

from knowde.integration.quiz.errors import (
    InvalidAnswerOptionError,
    QuizDuplicateError,
)
from knowde.shared.util import Neo4jDateTime

from .parts import QuizOption, QuizType


class ReadableQuiz(BaseModel, frozen=True):
    """「読める状態」の問題文と選択肢を備えたクイズ."""

    # 既に読める状態の問題文や選択肢
    quiz_id: UUID
    statement: str = Field(title="問題文")
    options: dict[str, str] = Field(title="選択肢")
    correct: list[str] = Field(title="正解")
    created: Neo4jDateTime

    @property
    def distractors(self) -> list[str]:
        """誤答肢."""
        return [op for op in self.options if op not in self.correct]

    @property
    def string(self) -> str:
        """問題文."""
        s = f"{self.statement}\n"
        ops = [indent(op, "  * ") for op in self.options.values()]
        s += "\n".join(ops)
        return s

    # TODO: 何も答えないのが正解、というパターンも欲しい  # noqa: FIX002, TD002, TD003
    def is_correct(self, selected: list[str]) -> bool:
        """正解かどうか."""
        for s in selected:
            if s not in self.options:
                msg = f"選択肢に存在しない回答; {s} not in {list(self.options.keys())}"
                raise InvalidAnswerOptionError(msg)
        s = set(selected)
        correct = set(self.correct)
        return s == correct


class QuizSource(BaseModel, frozen=True):
    """クイズ生成のための情報源.

    便利なgetterを備えるのみ
    """

    quiz_id: UUID
    quiz_type: QuizType  # build方法を指定してくれる
    target_id: str  # 答えになるとは限らない
    correct_ids: list[str] = Field(default_factory=list)
    sources: dict[str, QuizOption] = Field(title="クイズの元となるメンバ")
    created: Neo4jDateTime

    @model_validator(mode="after")
    def option_duplicate_check(self):
        """重複チェック."""
        options = list(self.sources.values())
        dups = list(duplicates_everseen(options))
        if len(dups) > 0:
            msg = f"同一のクイズ選択肢が指定されています: {dups}"
            raise QuizDuplicateError(msg)
        return self

    @property
    def target(self) -> QuizOption:
        """クイズ対象."""
        return self.sources[self.target_id]

    def get_id_by_sent(self, sent: str) -> str:
        """単文指定でidを返す."""
        key = next(
            (k for k in self.sources if self.sources[k].sentence == sent),
            None,
        )
        if key is None:
            msg = f"{sent} not found"
            raise KeyError(msg)
        return key

    def to_readable(self) -> ReadableQuiz:
        """読める状態にする."""
        options = {k: self.quiz_type.opt_answer(v) for k, v in self.sources.items()}
        correct_opts = [self.sources[c] for c in self.correct_ids]
        stmt = self.quiz_type.statement(self.target, correct_opts)
        return ReadableQuiz(
            quiz_id=self.quiz_id,
            statement=stmt,
            options=options,
            correct=self.quiz_type.correct_ids(self.target_id, self.correct_ids),
            created=self.created,
        )

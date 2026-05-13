"""quiz domain."""

from collections.abc import Callable
from textwrap import indent
from uuid import UUID

from more_itertools import duplicates_everseen
from pydantic import BaseModel, Field, RootModel, model_validator

from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.integration.quiz.errors import (
    InvalidAnswerOptionError,
    QuizDuplicateError,
    QuizOptionsMustBeDefError,
)
from knowde.shared.util import Neo4jDateTime

from .parts import QuizOption, QuizType


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

    @property
    def source_defs(self) -> dict[str, Def]:
        """誤答肢の定義."""
        dists = {k: v.val for k, v in self.sources.items()}
        defs = {k: v for k, v in dists.items() if isinstance(v, Def)}
        if len(defs) != len(dists):
            msg = "誤答肢に用語なし単文が含まれている"
            raise QuizOptionsMustBeDefError(msg)
        return defs

    @property
    def ids(self) -> set[str]:
        """選択肢ids."""
        # target_idとsource_idsで重複する場合があるのでsetにする
        return {*self.sources.keys(), self.target_id}

    def get_by_id(self, option_id: str) -> QuizOption:
        """Target or sourceを返す."""
        if option_id == self.target_id:
            return self.target
        return self.sources[option_id]

    def get_by_sent(self, sent: str) -> QuizOption:
        """単文指定でTarget or sourceを返す."""
        if sent == self.target.sentence:
            return self.target
        for option in self.sources.values():
            if sent == option.sentence:
                return option
        msg = f"{sent} not found"
        raise KeyError(msg)

    def get_id_by_sent(self, sent: str) -> str:
        """単文指定でidを返す."""
        key = next((k for k in self.ids if self.get_by_id(k).sentence == sent), None)
        if key is None:
            msg = f"{sent} not found"
            raise KeyError(msg)
        return key

    def filter_by(self, fn: Callable[[str], bool]) -> list[str]:
        """ソースを絞り込む."""
        return [k for k in self.ids if fn(k)]


class ReadableQuiz(BaseModel, frozen=True):
    """「読める状態」の問題文と選択肢を備えたクイズ."""

    # 既に読める状態の問題文や選択肢
    quiz_id: UUID
    statement: str = Field(title="問題文")
    options: dict[str, str] = Field(title="選択肢")
    # 順番が大事になる問題もあるかもしれない
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


class ReadableQuizList(RootModel[list[ReadableQuiz]]):
    """可読クイズリスト."""

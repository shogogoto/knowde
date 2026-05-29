"""quiz domain."""

import uuid
from datetime import datetime
from textwrap import indent
from typing import Self
from uuid import UUID

from more_itertools import duplicates_everseen
from pydantic import BaseModel, Field, model_validator

from knowde.feature.parsing.sysnet import SysNet
from knowde.integration.quiz.domain.rel import QuizRel
from knowde.integration.quiz.errors import (
    InvalidAnswerOptionError,
    QuizDuplicateError,
)
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.util import TZ, Neo4jDateTime

from .parts import QuizOption, QuizType


class ReadableQuiz(BaseModel, frozen=True):
    """「読める状態」の問題文と選択肢を備えたクイズ."""

    # 既に読める状態の問題文や選択肢
    quiz_id: UUID
    statement: str = Field(title="問題文")
    options: dict[str, str] = Field(title="選択肢")
    correct: list[str] = Field(title="正解")
    created: Neo4jDateTime
    no_correct_option: bool

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

    def is_correct(self, selected: list[str]) -> bool:
        """正解かどうか."""
        for s in selected:
            if s not in self.options:
                msg = f"選択肢に存在しない回答; {s} not in {list(self.options.keys())}"
                raise InvalidAnswerOptionError(msg)
        s = set(selected)
        correct = set(self.correct)
        if self.no_correct_option:
            correct = set()
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
    no_correct_option: bool = Field(default=False)

    @model_validator(mode="after")
    def duplicate_check(self):
        """重複チェック."""
        srcs = list(self.sources.values())
        dups = list(duplicates_everseen(srcs))
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

    def readable_options(self) -> dict[str, str]:
        """適切に選択肢を作成."""
        options = {k: self.quiz_type.opt_answer(v) for k, v in self.sources.items()}
        if not self.quiz_type.has_term:
            options = {k: v for k, v in options.items() if k != self.target_id}
        # print(options)
        # print(self.correct_ids)
        # print(self.no_correct_option)
        # if self.no_correct_option:
        #     options = {k: v for k, v in options.items() if k not in self.correct_ids}
        # print(options)
        return options

    def to_readable(self) -> ReadableQuiz:
        """読める状態にする."""
        correct_opts = [self.sources[c] for c in self.correct_ids]
        return ReadableQuiz(
            quiz_id=self.quiz_id,
            statement=self.quiz_type.statement(self.target, correct_opts),
            options=self.readable_options(),
            correct=self.correct_ids,
            created=self.created,
            no_correct_option=self.no_correct_option,
        )

    @classmethod
    def from_sysnet(
        cls,
        sn: SysNet,
        qt: QuizType,
        target_stc: str,
        source_stcs: list[str],  # 順に番号が割り振られる
        correct_stcs: list[str] | None = None,
    ) -> Self:
        """SysNetから作成してテストを完結に書けるようにする."""
        if correct_stcs is None:
            correct_stcs = []
        tgt = sn.get(target_stc)

        ops: dict[str, QuizOption] = {}
        target_id = "dummy"
        correct_ids: list[str] = []
        for i, s in enumerate(source_stcs, start=1):
            src = sn.get(s)
            if tgt == src:
                rels = []
                target_id = str(i)
            else:
                ets, is_forward = EdgeType.path2edgetypes(sn.g, target_stc, s)
                rels = QuizRel.of(ets, is_forward)
            op = QuizOption(val=src, rels=rels)
            ops[str(i)] = op
            if s in correct_stcs:
                correct_ids.append(str(i))
        return cls(
            quiz_id=uuid.uuid4(),
            quiz_type=qt,
            target_id=target_id,
            sources=ops,
            correct_ids=correct_ids,
            created=datetime.now(tz=TZ),
        )

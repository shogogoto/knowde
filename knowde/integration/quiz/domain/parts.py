"""構成要素となる部品."""

from __future__ import annotations

from collections.abc import Hashable, Sequence
from enum import StrEnum, auto
from operator import attrgetter
from typing import Self

from pydantic import BaseModel

from knowde.feature.parsing.primitive.mark import inject2placeholder
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.integration.quiz.errors import QuizOptionsMustBeDefError
from knowde.shared.types import UUIDy

from .rel import QuizRel


class QuizOption(BaseModel, frozen=True):
    """クイズ選択肢."""

    val: str | Def | Hashable
    rels: Sequence[QuizRel] | None = None

    @classmethod
    def create(  # noqa: D102
        cls,
        sentence: str,
        names: list[str] | None = None,
        rels: Sequence[QuizRel] | None = None,
    ) -> Self:
        val = Def.create(sentence, names=names)
        return cls(val=val, rels=rels)

    # @classmethod
    # def from_syselm(cls, elm: KNArg) -> Self:
    #     """SysNet要素から作成."""
    #     match elm:
    #         case Def():
    #             rels = EdgeType.path2edgetypes()
    #             return cls(val=elm, rels=elm.rels)
    #         # case
    #     return cls(val=elm, rels=elm.rels)

    @property
    def rels_stmt(self) -> str:
        """選択肢の関係の文言."""
        if self.rels is None:
            msg = "rel is None"
            raise ValueError(msg)
        return "の".join([str(r) for r in self.rels])

    @property
    def sentence(self) -> str:
        """単文表現."""
        if isinstance(self.val, Def):
            return str(self.val.sentence)
        return str(self.val)

    @property
    def def_(self) -> Def:
        """クイズ対象."""
        tgt = self.val
        if isinstance(tgt, Def):
            return tgt
        msg = "クイズ対象が用語を持たない"
        raise QuizOptionsMustBeDefError(msg)


QUIZ_PLACEHOLDER = "$@"


class QuizType(StrEnum):
    """問題文の種類.

    用語当てクイズ: 単文の用語を当てる
    単文当てクイズ: 用語の単文を当てる
    関係当てクイズ: 単文のペアの関係を当てる. 関係の選択肢
    ペア当てクイズ: 対象単文と特定の関係にある単文を当てる. 単文を列挙
    """

    SENT2TERM = auto()
    TERM2SENT = auto()
    PAIR2REL = auto()
    REL2PAIR = auto()

    @classmethod
    def from_statemet(cls, stmt: str) -> QuizType:  # noqa: D102
        if stmt.endswith("に合う用語を当ててください"):
            return cls.SENT2TERM
        if stmt.endswith("に合う文を当ててください"):
            return cls.TERM2SENT
        if stmt.endswith("関係で繋がる単文を当ててください"):
            return cls.REL2PAIR
        if stmt.endswith("への関係を当ててください"):
            return cls.PAIR2REL
        msg = f"Unknown statement: {stmt}"
        raise ValueError(msg)

    @property
    def _TEMPLATE(self) -> str:  # noqa: N802
        return {
            QuizType.SENT2TERM: "$@に合う用語を当ててください",
            QuizType.TERM2SENT: "$@に合う文を当ててください",
            QuizType.REL2PAIR: "$@と$@関係で繋がる単文を当ててください",
            QuizType.PAIR2REL: "$@から$@への関係を当ててください",
        }[self]

    @property
    def _OPT_ANSWER(self) -> str:  # noqa: N802
        return {
            QuizType.SENT2TERM: "def_.term",
            QuizType.TERM2SENT: "def_.sentence",
            QuizType.REL2PAIR: "sentence",
            QuizType.PAIR2REL: "rels_stmt",
        }[self]

    @property
    def _OPT_QUESTION(self) -> str:  # noqa: N802
        return {
            QuizType.SENT2TERM: "def_.sentence",
            QuizType.TERM2SENT: "def_.term",
            QuizType.REL2PAIR: "rels_stmt",
            QuizType.PAIR2REL: "sentence",
        }[self]

    @property
    def has_term(self) -> bool:
        """用語あり単文が選択肢."""
        return self in {QuizType.SENT2TERM, QuizType.TERM2SENT}

    def opt_answer(self, opt: QuizOption) -> str:
        """回答表現の選択肢."""
        return str(attrgetter(self._OPT_ANSWER)(opt))

    def correct_ids(
        self,
        target_id: UUIDy,
        correct_ids: list[UUIDy] | None = None,
    ) -> list[UUIDy]:
        """正解を決定する."""
        if correct_ids is None:
            correct_ids = []
        if self.has_term:
            return [str(target_id)]
        return [str(i) for i in correct_ids]

    def opt_question(self, opt: QuizOption) -> str:
        """問題文表現の選択肢."""
        return str(attrgetter(self._OPT_QUESTION)(opt))

    def statement(self, target: QuizOption, corrects: list[QuizOption]) -> str:
        """クイズの問題文."""
        if self.has_term:
            vals = [self.opt_question(target)]
        else:
            vals = [str(target.val), *[self.opt_question(c) for c in corrects]]
        return self.inject(vals)

    def inject(self, vals: list[str]) -> str:
        """プレースホルダーを置き換えて返す."""
        return inject2placeholder(
            self._TEMPLATE,
            vals,
            QUIZ_PLACEHOLDER,
            surround_pre="'",
            surround_post="'",
        )

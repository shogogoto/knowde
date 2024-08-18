"""domain."""
from __future__ import annotations

from textwrap import indent
from typing import Self

from pydantic import BaseModel, Field

from knowde._feature.proposition.domain import Proposition  # noqa: TCH001
from knowde.core.domain import APIReturn, Entity


class Deduction(Entity, frozen=True):
    """演繹."""

    text: str = Field(title="文章")
    premises: list[Proposition] = Field(
        default_factory=list,
        title="前提",
    )
    conclusion: Proposition = Field(title="結論")
    valid: bool = Field(description="結論の正しさ")

    @property
    def output(self) -> str:
        """For CLI output."""
        s = f"{self.text} ({self.valid_uid})"
        s += "\n" + indent(self.conclusion.output, ":")
        for pre in self.premises:
            s += "\n" + indent(pre.output, " " * 2)
        return s


class DeductionStatistics(BaseModel, frozen=True):
    """演繹統計."""

    n_src: int = Field(title="元数")
    n_dest: int = Field(title="先数")
    n_axiom: int = Field(title="公理数")
    n_leaf: int = Field(title="葉数", description="先頭の数")
    max_axiom_dist: int = Field(title="最大公理距離")
    max_leaf_dist: int = Field(title="最大葉距離")

    @classmethod
    def create(cls, nums: list[int]) -> Self:
        """Create from nums."""
        if len(nums) != 6:  # noqa: PLR2004
            msg = "nums must be int list of 6 length"
            raise ValueError(msg)
        return cls(
            n_src=nums[0],
            n_dest=nums[1],
            n_axiom=nums[2],
            n_leaf=nums[3],
            max_axiom_dist=nums[4],
            max_leaf_dist=nums[5],
        )

    @property
    def nums(self) -> tuple[int, int, int, int, int, int]:
        """For test convinency."""
        return (
            self.n_src,
            self.n_dest,
            self.n_axiom,
            self.n_leaf,
            self.max_axiom_dist,
            self.max_leaf_dist,
        )

    @property
    def output(self) -> str:
        """For CLI output."""
        return "ns:{}, nd:{}, na:{}, nl:{}, mad:{}, mld:{}".format(*self.nums)


class StatsDeduction(BaseModel, frozen=True):
    """統計付き演繹."""

    deduction: Deduction
    stats: DeductionStatistics

    @property
    def output(self) -> str:
        """Str for CLI."""
        d = self.deduction
        s = d.updated.strftime("%y/%m/%d")
        st = self.stats
        return f"{st.output} {s}\n{d.output}"


class StatsDeductions(APIReturn, frozen=True):
    """統計付き演繹リスト."""

    values: list[StatsDeduction] = Field(default_factory=list)

    @property
    def deductions(self) -> list[Deduction]:
        """Deduction list."""
        return [v.deduction for v in self.values]

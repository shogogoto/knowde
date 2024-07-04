"""domain."""
from __future__ import annotations

from typing import Self

from pydantic import BaseModel, Field

from knowde._feature._shared.domain import APIReturn, Entity


class Proposition(Entity, frozen=True):
    """命題."""

    text: str = Field(title="文章")


class Deduction(Entity, frozen=True):
    """演繹."""

    text: str = Field(title="文章")
    premises: list[Proposition] = Field(
        default_factory=list,
        title="前提",
    )
    conclusion: Proposition = Field(title="結論")
    valid: bool = Field(description="結論の正しさ")


class DeductionStatistics(BaseModel, frozen=True):
    """演繹統計."""

    n_src: int
    n_dest: int
    n_axiom: int
    n_leaf: int
    max_axiom_dist: int
    max_leaf_dist: int

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
        """For test conviniency."""
        return (
            self.n_src,
            self.n_dest,
            self.n_axiom,
            self.n_leaf,
            self.max_axiom_dist,
            self.max_leaf_dist,
        )


class StatsDeduction(BaseModel, frozen=True):
    """統計付き演繹."""

    deduction: Deduction
    stats: DeductionStatistics


class StatsDeductions(APIReturn, frozen=True):
    """統計付き演繹リスト."""

    values: list[StatsDeduction] = Field(default_factory=list)

    @property
    def deductions(self) -> list[Deduction]:
        """Deduction list."""
        return [v.deduction for v in self.values]

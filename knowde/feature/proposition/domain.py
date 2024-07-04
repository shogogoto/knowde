"""domain."""
from __future__ import annotations

from pydantic import BaseModel, Field

from knowde._feature._shared.domain import Entity


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

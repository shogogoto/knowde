"""依存統計."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from knowde.primitive.__core__.domain import APIReturn

if TYPE_CHECKING:
    from knowde.tmp.definition.domain.domain import Definition


class DepStatistics(BaseModel, frozen=True):
    """依存関係の統計."""

    n_src: int = Field(default=0, description="依存元数")
    n_dest: int = Field(default=0, description="依存先数")
    max_root_dist: int = Field(default=0, description="最大root距離")
    max_leaf_dist: int = Field(default=0, description="最大leaf距離")

    @property
    def nums(self) -> tuple[int, int, int, int]:
        """For testing easy."""
        return (
            self.n_src,
            self.n_dest,
            self.max_leaf_dist,
            self.max_root_dist,
        )

    @property
    def output(self) -> str:
        """For cli output."""
        ns = self.n_src
        nd = self.n_dest
        mld = self.max_leaf_dist
        mrd = self.max_root_dist
        return f"ns:{ns}, nd:{nd}, mld:{mld}, mrd:{mrd}"


class StatsDefinition(APIReturn, frozen=True):
    """統計付き定義."""

    definition: Definition
    statistics: DepStatistics

    @property
    def output(self) -> str:
        """Output for cli."""
        do = self.definition.output
        so = self.statistics.output
        return f"{do} {so}"


class StatsDefinitions(APIReturn, frozen=True):
    """リストの統計付き定義."""

    values: list[StatsDefinition] = Field(default_factory=list)

    @property
    def defs(self) -> list[Definition]:
        """Def list."""
        return [sd.definition for sd in self.values]

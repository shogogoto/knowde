"""依存統計."""
from __future__ import annotations

from pydantic import BaseModel, Field, RootModel

from knowde._feature._shared.domain import APIReturn
from knowde.feature.definition.domain.domain import Definition  # noqa: TCH001


class DepStatistics(BaseModel, frozen=True):
    """依存関係の統計."""

    n_src: int = Field(description="依存元数")
    n_dest: int = Field(description="依存先数")
    max_root_dist: int = Field(description="最大root距離")
    max_leaf_dist: int = Field(description="最大leaf距離")

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


class StatsDefinitions(RootModel[list[StatsDefinition]], frozen=True):
    """リストの統計付き定義."""

    def defs(self) -> list[Definition]:
        """Def list."""
        return [sd.definition for sd in self.root]

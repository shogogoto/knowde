"""依存統計."""
from __future__ import annotations

from pydantic import BaseModel, Field


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

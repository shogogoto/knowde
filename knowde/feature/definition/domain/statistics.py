"""依存統計."""
from pydantic import BaseModel, Field


class DepStatistics(BaseModel, frozen=True):
    """依存関係の統計."""

    n_deps: int = Field(description="依存定義数")
    n_roots: int = Field(description="依存定義")
    max_root_dist: int = Field(description="最大root距離")
    max_leaf_dist: int = Field(description="最大leaf距離")

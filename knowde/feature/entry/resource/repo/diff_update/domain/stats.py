"""更新差分の集計."""

from pydantic import BaseModel


class UpdateDiffStats(BaseModel, frozen=True):
    """更新差分集計."""

    @classmethod
    def create(cls):
        """ファクトリ."""
        return cls()

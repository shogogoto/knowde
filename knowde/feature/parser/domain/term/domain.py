"""用語モデル."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TermGroup(BaseModel, frozen=True):
    """特定の言明に割り当てられた用語のグループ."""

    rep: str = Field(title="代表名")  # representativeが長いので略
    aliases: list[str] = Field(default_factory=list)

    def __str__(self) -> str:
        """Display for user."""
        al = ", ".join(self.aliases)
        if len(al) > 0:
            al = f"({al})"
        return f"{self.rep}{al}"

"""ASTのnode."""
from enum import Enum, auto

from pydantic import BaseModel, Field


class ContextType(Enum):
    """文脈の種類."""

    THUS = auto()
    CAUSE = auto()
    ANTONYM = auto()
    EXAMPLE = auto()
    GENERAL = auto()
    REF = auto()
    NUM = auto()
    SIMILAR = auto()
    WHEN = auto()
    BY = auto()
    EQUIV = auto()


class Comment(BaseModel, frozen=True):
    """コメント."""

    value: str

    def __str__(self) -> str:
        """For user string."""
        return f"!{self.value}"


class Heading(BaseModel, frozen=True):
    """見出しまたは章節."""

    title: str
    level: int = Field(ge=1, le=6)

    def __str__(self) -> str:
        """For user string."""
        return f"h{self.level}={self.title}"

    def contains(self, title: str) -> bool:
        """タイトルを含んでいるか."""
        return title in self.title

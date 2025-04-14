"""情報の基本単位."""

from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field

from knowde.complex.nxdb import LSentence
from knowde.primitive.term import Term
from knowde.primitive.user import User

"""
  adjacent 直近の周辺情報
    as logic
      premises -> self
      conclusions <- self
    as term
      refer この文が引用する文 参照 -> self
      referred この文が引用している文 被参照 <- self
    as part
      detail
      parent

DB 検索
term: sentでマッチ
その文脈を加える


"""


class Knowde(BaseModel, frozen=True):
    """知識の最小単位."""

    sentence: str
    uid: UUID
    term: Term | None = None

    @classmethod
    def of(cls, lb: LSentence) -> Self:
        """LSentenceから知識を取得."""
        return cls(
            sentence=str(lb.val),
            uid=lb.uid,
        )

    def __str__(self) -> str:  # noqa: D105
        t = f"[{self.term}]" if self.term else ""
        return f"{self.sentence}{t}"


class KLocation(BaseModel):
    """知識の位置情報."""

    owner: User
    path: tuple[str, ...]


class KAdjacency(BaseModel):
    """周辺情報も含める."""

    center: Knowde
    when: str | None = None
    details: list[Knowde] = Field(default_factory=list)
    premises: list[Knowde] = Field(default_factory=list)
    conclusions: list[Knowde] = Field(default_factory=list)
    refers: list[Knowde] = Field(default_factory=list)
    referreds: list[Knowde] = Field(default_factory=list)

    def __str__(self) -> str:
        """For display in CLI."""
        s = str(self.center)
        s += f"@{self.when}" if self.when else ""
        if self.details:
            s += f"  {{ {', '.join(map(str, self.details))} }}"
        if self.premises:
            s += f"\n<- {', '.join(map(str, self.premises))}"
        if self.conclusions:
            s += f"\n-> {', '.join(map(str, self.conclusions))}"
        if self.refers:
            s += f"\n<< {', '.join(map(str, self.refers))}"
        if self.referreds:
            s += f"\n>> {', '.join(map(str, self.referreds))}"
        return s

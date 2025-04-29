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


class KStats(BaseModel):
    """知識の関係統計."""

    # frontendのモック自動生成で数値の範囲を制限したい
    n_detail: int = Field(ge=-100, le=1000)
    n_premise: int = Field(ge=-100, le=1000)
    n_conclusion: int = Field(ge=-100, le=1000)
    n_refer: int = Field(ge=-100, le=1000)
    n_referred: int = Field(ge=-100, le=1000)
    dist_axiom: int = Field(ge=-100, le=1000)
    dist_leaf: int = Field(ge=-100, le=1000)
    score: int | None = Field(default=None, ge=-100, le=1000)

    def __str__(self) -> str:  # noqa: D105
        ls = [
            self.n_detail,
            self.n_premise,
            self.n_conclusion,
            self.n_refer,
            self.n_referred,
            self.dist_axiom,
            self.dist_leaf,
            self.score,
        ]
        return str(ls)


class KAdjacency(BaseModel):
    """周辺情報も含める."""

    center: Knowde
    when: str | None = None
    details: list[Knowde] = Field(default_factory=list)
    premises: list[Knowde] = Field(default_factory=list)
    conclusions: list[Knowde] = Field(default_factory=list)
    refers: list[Knowde] = Field(default_factory=list)
    referreds: list[Knowde] = Field(default_factory=list)
    stats: KStats | None = None

    def __str__(self) -> str:
        """For display in CLI."""
        s = str(self.center)
        s += f"@{self.when}" if self.when else ""
        s += "\n" + str(self.stats) if self.stats else ""
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

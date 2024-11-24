"""系ネットワークのノード."""
from __future__ import annotations

from typing import TYPE_CHECKING, Self, TypeAlias
from uuid import uuid4

from pydantic import BaseModel, Field

from knowde.primitive.term import Term

if TYPE_CHECKING:
    from uuid import UUID


class Def(BaseModel, frozen=True):
    """定義."""

    term: Term
    sentence: str

    @classmethod
    def create(cls, sentence: str, names: list[str], alias: str | None = None) -> Self:
        """便利コンストラクタ."""
        t = Term.create(*names, alias=alias)
        return cls(term=t, sentence=sentence)

    def __repr__(self) -> str:  # noqa: D105
        return str(self)

    def __str__(self) -> str:  # noqa: D105
        return f"{self.term}: {self.sentence}"


SysNode: TypeAlias = Term | str
SysArg: TypeAlias = SysNode | Def


class Duplicable(BaseModel, frozen=True):
    """コメントや区分け文字列.

    区分け文字 みたいな区切りを作るためだけの無意味な文字列の扱いは?
    同一文字列は重複して登録できない.
    なので、uuidを付与する
    """

    n: str
    uid: UUID = Field(default_factory=uuid4)

    def __str__(self) -> str:  # noqa: D105
        return str(self.n)

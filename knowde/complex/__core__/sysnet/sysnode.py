"""系ネットワークのノード."""
from __future__ import annotations

from functools import cache
from typing import Self, TypeAlias
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from knowde.primitive.term import Term


class Def(BaseModel, frozen=True):
    """定義."""

    term: Term
    sentence: str | DummySentence

    @classmethod
    def create(cls, sentence: str, names: list[str], alias: str | None = None) -> Self:
        """便利コンストラクタ."""
        t = Term.create(*names, alias=alias)
        return cls(term=t, sentence=sentence)

    def __repr__(self) -> str:  # noqa: D105
        return str(self)

    def __str__(self) -> str:  # noqa: D105
        return f"{self.term}: {self.sentence}"

    @classmethod
    @cache
    def dummy(cls, t: Term) -> Self:
        """Create vacuous def."""
        return cls(term=t, sentence=DummySentence())


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

    def __eq__(self, other: Self) -> bool:  # noqa: D105
        return str(self) == str(other)


class DummySentence(Duplicable, frozen=True):
    """Termのみの場合に擬似的に定義とみなすための空文字列."""

    n: str = "<<<not defined>>>"


SysNode: TypeAlias = Term | str | Duplicable
SysArg: TypeAlias = SysNode | Def

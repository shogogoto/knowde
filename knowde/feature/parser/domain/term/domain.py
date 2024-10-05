"""用語モデル."""
from __future__ import annotations

from collections import Counter
from typing import Self

from pydantic import BaseModel, Field, field_validator


class Term(BaseModel, frozen=True):
    """用語 名前のあつまり."""

    names: list[str] = Field(default_factory=list, min_length=1)

    @field_validator("names")
    @classmethod
    def _validate(cls, vs: list[str]) -> list[str]:
        """Validate duplication."""
        for k, v in Counter(vs).items():
            if v > 1:
                msg = f"{k}が複数回{v}宣言されています"
                raise ValueError(msg)
        return vs

    @property
    def rep(self) -> str:
        """代表名."""
        return self.names[0]

    @property
    def aliases(self) -> list[str]:
        """別名リスト."""
        return self.names[1:]

    @classmethod
    def create(cls, *vs: str) -> Self:  # noqa: D102
        return cls(names=list(vs))

    def __str__(self) -> str:
        """Display for user."""
        al = ", ".join(self.aliases)
        if len(al) > 0:
            al = f"({al})"
        return f"{self.rep}{al}"

    def has(self, *names: str) -> bool:
        """同じ名前を持つ."""
        s1 = set(self.names)
        s2 = set(names)
        common = s1.intersection(s2)
        return len(common) > 0

    def has_only_name(self) -> bool:
        """単名を持つ."""
        return len(self.names) == 1

    def allows_merge(self, other: Term) -> bool:
        """合併を許すか否か."""
        # 共通なし -> 合併しない
        # 共通あり
        #   完全一致 -> False
        #     -> True
        if not self.has(*other.names):
            return False
        # if self == other:
        #     return False
        # return True
        has_only = self.has_only_name() or other.has_only_name()
        return not has_only

    def merge(self, other: Term) -> Term:
        """名前を併せた用語へ."""
        if not self.allows_merge(other):
            raise TermMergeError(self, other)
        s1 = set(self.names)
        s2 = set(other.names)
        diff = s2.difference(s1)
        return Term(names=self.names + list(diff))

    @property
    def d(self) -> dict[str, Self]:
        """HashMapによる検索に使えるかな."""
        return {k: self for k in self.names}


class TermMergeError(Exception):
    """用語の合併を許さないのに."""


class TermConflictError(Exception):
    """用語の衝突."""


class TermSpace(BaseModel):
    """用語空間.

    名前一覧を表現
    名前 -> 用語

    """

    terms: list[Term] = Field(default_factory=list)
    origins: list[Term] = Field(default_factory=list)

    def __getitem__(self, i: int) -> Term:  # noqa: D105
        return self.terms[i]

    def __len__(self) -> int:  # noqa: D105
        return len(self.terms)

    def add(self, t: Term) -> None:
        """名前."""
        if t in self.origins:
            msg = "用語定義が重複しています"
            raise TermConflictError(msg, t)
        c = self.common(t)
        if c is None:
            self.terms.append(t)
        else:
            self.terms.remove(c)
            self.terms.append(c.merge(t))
        self.origins.append(t)

    def common(self, t: Term) -> Term | None:
        """共通する名を持つ用語があれば返す."""
        ls = [v for v in self.terms if t.has(*v.names)]
        match len(ls):
            case 0:
                return None
            case 1:
                return ls[0]
            case _:
                raise TermConflictError

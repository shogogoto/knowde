"""用語モデル."""
from __future__ import annotations

from collections import Counter
from typing import Self

from pydantic import BaseModel, Field, field_validator

from .errors import TermConflictError, TermMergeError


class Term(BaseModel, frozen=True):
    """用語."""

    names: list[str] = Field(default_factory=list)
    alias: str | None = Field(
        default=None,
        title="別名",
        description="参照用の無意味な記号",
    )

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
        return "" if len(self.names) == 0 else self.names[0]

    @classmethod
    def create(cls, *vs: str, alias: str | None = None) -> Self:  # noqa: D102
        return cls(names=list(vs), alias=alias)

    def __str__(self) -> str:
        """Display for user."""
        subs = ", ".join(self.names[1:])
        if len(subs) > 0:
            subs = f"({subs})"
        al = ""
        if self.alias is not None:
            al = f"[{self.alias}]"
        return f"{self.rep}{subs}{al}"

    def has(self, *names: str) -> bool:
        """同じ名前を持つ."""
        s1 = set(self.names)
        s2 = set(names)
        common = s1.intersection(s2)
        return len(common) > 0

    def allows_merge(self, other: Term) -> bool:
        """合併を許すか否か."""
        if not self.has(*other.names):
            return False
        if set(self.names) == set(other.names):
            return False
        if self.alias and other.alias:
            return False
        only_self = len(self.names) == 1 or len(other.names) > 1
        only_other = len(self.names) > 1 or len(other.names) == 1
        return only_self or only_other

    def merge(self, other: Term) -> Term:
        """名前を併せた用語へ."""
        if not self.allows_merge(other):
            raise TermMergeError(self, other)
        s1 = set(self.names)
        s2 = set(other.names)
        diff = s2.difference(s1)
        return Term(names=self.names + list(diff))

    def has_only_alias(self) -> bool:
        """別名しか持たない."""
        return len(self.names) == 0 and self.alias is not None


class MergedTerms(BaseModel):
    """用語一覧."""

    terms: list[Term] = Field(default_factory=list)
    origins: list[Term] = Field(default_factory=list)

    def __getitem__(self, i: int) -> Term:  # noqa: D105
        return self.terms[i]

    def __len__(self) -> int:
        """名前を持つ用語の数."""
        return len([t for t in self.terms if not t.has_only_alias()])

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

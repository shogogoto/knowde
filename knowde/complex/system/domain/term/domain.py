"""用語モデル."""
from __future__ import annotations

from collections import Counter
from functools import cached_property
from typing import Self

from networkx import DiGraph
from pydantic import BaseModel, Field, field_validator

from knowde.complex.system.domain.term.mark import contains_mark_symbol

from .errors import AliasContainsMarkError, TermConflictError, TermMergeError


class Term(BaseModel, frozen=True):
    """用語."""

    names: frozenset[str] = Field(default_factory=frozenset)
    alias: str | None = Field(
        default=None,
        title="別名",
        description="参照用の無意味な記号",
    )
    rep: str = Field(default="", title="代表名")

    @field_validator("names")
    @classmethod
    def _validate(cls, vs: list[str]) -> list[str]:
        """Validate duplication."""
        for k, v in Counter(vs).items():
            if v > 1:
                msg = f"{k}が複数回{v}宣言されています"
                raise ValueError(msg)
        return vs

    @field_validator("alias")
    @classmethod
    def _validate_alias(cls, v: str | None) -> str | None:
        """Validate duplication."""
        if v is not None and contains_mark_symbol(v):
            msg = "aliasにMARK文字が含まれています"
            raise AliasContainsMarkError(msg)
        return v

    @classmethod
    def create(cls, *vs: str, alias: str | None = None) -> Self:  # noqa: D102
        match len(vs):
            case 0:
                return cls(names=frozenset(vs), alias=alias)
            case _:
                return cls(names=frozenset(vs), alias=alias, rep=vs[0])

    def __str__(self) -> str:
        """Display for user."""
        subs = ", ".join(self.names - set(self.rep))
        if len(subs) > 0:
            subs = f"({subs})"
        al = ""
        if self.alias is not None:
            al = f"[{self.alias}]"
        rep = "" if len(self.names) == 0 else self.rep
        return f"{rep}{subs}{al}"

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
        s1 = self.names
        s2 = other.names
        diff = s2.difference(s1)
        return Term(
            names=frozenset.union(self.names, diff),
            alias=self.alias,
            rep=self.rep,
        )


class MergedTerms(BaseModel, frozen=True):
    """用語一覧."""

    terms: list[Term] = Field(default_factory=list)
    origins: list[Term] = Field(default_factory=list, init=False)

    def __getitem__(self, i: int) -> Term:  # noqa: D105
        return self.terms[i]

    def __len__(self) -> int:
        """名前を持つ用語の数."""
        return len(self.terms)

    def add(self, *ts: Term) -> None:
        """用語を追加する."""
        for t in ts:
            if t in self.origins:
                msg = "用語定義が重複しています"
                raise TermConflictError(msg, t)
            c = self._common(t)
            if c is None:
                self.terms.append(t)
            else:
                self.terms.remove(c)
                self.terms.append(c.merge(t))
            self.origins.append(t)

    def _common(self, t: Term) -> Term | None:
        """共通する名を持つ用語があれば返す."""
        ls = [v for v in self.terms if t.has(*v.names)]
        match len(ls):
            case 0:
                return None
            case 1:
                return ls[0]
            case _:
                raise TermConflictError

    @cached_property
    def atomic_terms(self) -> dict[str, Term]:
        """参照なしの原子用語."""
        d = {}
        for t in self.terms:
            if t.alias:
                d[t.alias] = t
            for n in t.names:
                if not contains_mark_symbol(n):
                    d[n] = t
        return d


def molecular_terms(_mt: MergedTerms) -> DiGraph[str]:
    """参照有りの分子用語."""
    # d = {}
    # atoms = mt.atomic_terms.values()
    # print(set(atoms))
    # for t in set(mt.terms) - atoms:
    #     print(t)
    #     for n in t.names:
    #         if not contains_mark_symbol(n):
    #             d[n] = t
    #     if t.alias:
    #         d[t.alias] = t

    return DiGraph()


# class TermNetwork(BaseModel, frozen=True):
#     """用語ネットワーク."""

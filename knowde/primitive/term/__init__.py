"""用語モデル."""
from __future__ import annotations

from collections import Counter
from functools import cached_property
from typing import AbstractSet, Iterable, NoReturn, Self

import networkx as nx
from pydantic import BaseModel, Field, PrivateAttr, field_validator

from knowde.primitive.__core__.dupchk import DuplicationChecker
from knowde.primitive.__core__.nxutil import EdgeType, to_nested
from knowde.primitive.__core__.types import NXGraph

from .errors import (
    AliasContainsMarkError,
    MarkUncontainedError,
    TermConflictError,
    TermMergeError,
    TermResolveError,
)
from .mark import (
    contains_mark_symbol,
    pick_marks,
    replace_markers,
)


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
    def create(cls, *names: str, alias: str | None = None) -> Self:  # noqa: D102
        match len(names):
            case 0:
                return cls(names=frozenset(names), alias=alias)
            case _:
                return cls(names=frozenset(names), alias=alias, rep=names[0])

    def __repr__(self) -> str:
        """Class representation."""
        return f"Term({self})"

    def __str__(self) -> str:
        """Display for user."""
        subs = ", ".join(self.names - {self.rep})
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

    @property
    def has_only_alias(self) -> bool:
        """aliasのみ."""
        return self.alias and len(self.names) == 0

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


def term_dup_checker() -> DuplicationChecker:
    """用語重複チェッカー."""

    def _err(t: Term) -> NoReturn:
        msg = f"用語'{t}'が重複しています"
        raise TermConflictError(msg)

    return DuplicationChecker(err_fn=_err)


class MergedTerms(BaseModel, frozen=True):
    """用語一覧."""

    terms: list[Term] = Field(default_factory=list, init=False)
    _chk: DuplicationChecker = PrivateAttr(
        default_factory=term_dup_checker,
    )

    def __getitem__(self, i: int) -> Term:  # noqa: D105
        return self.terms[i]

    def __len__(self) -> int:
        """名前を持つ用語の数."""
        return len(self.terms)

    def add(self, *ts: Term) -> Self:
        """用語を追加する."""
        for t in ts:
            self._chk(t)
            c = self._common(t)
            if c is None:
                self.terms.append(t)
            else:
                self.terms.remove(c)
                self.terms.append(c.merge(t))
        return self

    def _common(self, t: Term) -> Term | None:
        """共通する名を持つ用語があれば返す."""
        ls = [v for v in self.terms if t.has(*v.names)]
        match len(ls):
            case 0:
                return None
            case 1:
                return ls[0]
            case _:
                msg = "重複によってマージできませんでした"
                raise TermConflictError(msg, ls)

    @cached_property
    def atoms(self) -> dict[str, Term]:
        """参照{}を含まない用語."""
        d = {}
        for t in self.terms:
            if t.alias:
                d[t.alias] = t
            for n in t.names:
                if not contains_mark_symbol(n):
                    d[n] = t
        return d

    @cached_property
    def frozen(self) -> frozenset[Term]:
        """Frozen merged terms."""
        return frozenset(self.terms)

    def to_resolver(self) -> TermResolver:
        """用語ネットワーク作成."""
        g = nx.DiGraph()
        lookup = self.atoms
        g.add_nodes_from(lookup.keys())
        while True:
            _next, diff = next_lookup(lookup, self.frozen)
            for t in _next.values():
                for n in t.names:
                    marks = pick_marks(n)
                    atom = replace_markers(n, *marks)
                    for m in marks:
                        g.add_edge(atom, m)
            d = {**lookup, **_next}
            if lookup == d:
                n_diff = len(diff)
                break
            lookup = d
        if n_diff > 0:
            msg = f"{set(diff)}が用語解決できませんでした"
            raise TermResolveError(msg)
        return TermResolver(g=g, lookup=lookup)


# lookup {name: Term}辞書
#  nameに引用がある
#  nameに引用がない
def next_lookup(
    lookup: dict[str, Term],
    terms: AbstractSet[Term],
) -> tuple[dict[str, Term], AbstractSet[Term]]:
    """直参照の用語lookupを取得."""
    diff = terms - set(lookup.values())
    d = {}
    for t in diff:
        for n in t.names:
            marks = pick_marks(n)
            if all(m in lookup for m in marks):
                atom = replace_markers(n, *marks)
                d[atom] = t
        if t.alias:
            d[t.alias] = t
    return d, diff


class TermResolver(BaseModel, frozen=True):
    """用語解決器."""

    g: NXGraph
    lookup: dict[str, Term]  # {name: Term}辞書

    def __call__(self, s: str) -> dict:
        """任意の文字列を用語解決.

        Return:
        ------
            {mark: {mark:{...:{}}}}

        """
        marks = pick_marks(s)
        for m in marks:
            if m not in self.g:
                msg = f"'{m}'は用語として存在しません at {s}"
                raise MarkUncontainedError(msg)
        return {m: to_nested(self.g, m, lambda g, n: g.successors(n)) for m in marks}

    def mark2term(self, md: dict) -> dict:
        """markに対応する用語に変換する.

        Return:
        ------
            {term: {term:{...:{}}}}

        """
        d = {}
        for k, v in md.items():
            t = self.lookup[k]
            if any(v):  # 空でない
                d[t] = self.mark2term(v)
            else:
                d[t] = v
        return d

    def add_edges(self, g: nx.DiGraph, sentences: Iterable[str]) -> None:
        """文とそこに埋めこられた用語を関係付ける."""
        for s in sentences:
            d = self(s)
            td = self.mark2term(d)
            _add_resolve_edge(g, s, td)


def _add_resolve_edge(g: nx.DiGraph, start: str, termd: dict) -> None:
    """(start)-[RESOLVE]->(marked sentence)."""
    for k, v in termd.items():
        ls = list(EdgeType.DEF.succ(g, k))
        if len(ls) == 0:
            continue
        s = ls[0]  # 文
        EdgeType.RESOLVED.add_edge(g, start, s)  # 文 -> 文
        if any(v):  # 空でない
            _add_resolve_edge(g, str(s), v)


def resolve_sentence(g: nx.DiGraph, s: str) -> dict:
    """解決済み入れ子文を取得."""
    return to_nested(g, s, EdgeType.RESOLVED.succ)

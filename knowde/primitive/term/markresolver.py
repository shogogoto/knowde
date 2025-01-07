"""mark解決器."""
from __future__ import annotations

from typing import Self

from pydantic import BaseModel

from knowde.primitive.__core__.nxutil import to_nested
from knowde.primitive.__core__.types import NXGraph
from knowde.primitive.term import MergedTerms, Term
from knowde.primitive.term.errors import MarkUncontainedError
from knowde.primitive.term.mark.domain import pick_marks


class MarkResolver(BaseModel, frozen=True):
    """mark解決器."""

    g: NXGraph  # mark network
    lookup: dict[str, Term]  # {mark: Term}辞書

    @classmethod
    def create(cls, mt: MergedTerms) -> Self:
        """Create instance."""
        g, lookup = mt.to_resolver()
        return cls(g=g, lookup=lookup)

    def sentence2marktree(self, s: str) -> dict[str, str | dict]:
        """任意の文字列を用語解決 mark dict tree.

        Return:
        ------
            {mark: {mark:{...:{}}}}

        """
        marks = pick_marks(s)
        for m in marks:
            if m not in self.g:
                msg = f"'{m}'は用語として存在しません at '{s}'"
                raise MarkUncontainedError(msg)
        return {m: to_nested(self.g, m, lambda g, n: g.successors(n)) for m in marks}

    def mark2term(self, md: dict) -> dict[Term, dict]:
        """markに対応する用語に変換する.

        Return:
        ------
            {Term: {Term:{...:{}}}}

        """
        d = {}
        for k, v in md.items():
            t = self.lookup[k]
            if any(v):  # 空でない
                d[t] = self.mark2term(v)
            else:
                d[t] = v
        return d

    def term2marktree(self, t: Term) -> dict[str, str | dict]:
        """用語を用語解決."""
        marks = [k for k, v in self.lookup.items() if v == t]
        return {m: to_nested(self.g, m, lambda g, n: g.successors(n)) for m in marks}

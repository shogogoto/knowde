"""用語Visitor."""
from __future__ import annotations

from lark import Token, Tree
from pydantic import Field

from knowde.feature.parser.domain.parser.const import ALIAS_TYPE
from knowde.feature.parser.domain.parser.utils import HeadingVisitor
from knowde.feature.parser.domain.term.domain import (
    Term,
    TermConflictError,
    TermMergeError,
    TermSpace,
)


class TermVisitor(HeadingVisitor):
    """用語を集める."""

    space: TermSpace = Field(default_factory=TermSpace)

    def alias_line(self, t: Tree) -> None:  # noqa: D102
        alias = t.children[0]
        term = Term(alias=alias)
        self._add_term(term)

    def name(self, t: Tree) -> None:  # noqa: D102
        alias, names = self._get_alias_names(t)
        term = Term(names=names, alias=alias)
        self._add_term(term)

    def _add_term(self, term: Term) -> None:
        try:
            self.space.add(term)
        except TermMergeError as e:
            msg = f"{self.current}で{e}"
            raise TermMergeError(msg) from e
        except TermConflictError as e:
            msg = f"{self.current}で{e}"
            raise TermConflictError(msg) from e

    def _get_alias_names(self, t: Tree) -> tuple[str | None, list[str]]:
        """aliasを取得."""
        c = t.children
        f = c[0]
        if isinstance(f, Token) and f.type == ALIAS_TYPE:
            return f, c[1:]
        return None, c


def get_termspace(t: Tree) -> TermSpace:
    """用語空間を抜き出す."""
    v = TermVisitor()
    v.visit_topdown(t)
    return v.space

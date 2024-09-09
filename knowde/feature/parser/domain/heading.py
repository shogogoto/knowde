"""textから章節を抜き出す."""
from __future__ import annotations

import functools
from typing import Callable

from lark import Token, Transformer, Tree
from pydantic import BaseModel, Field


def _is_heading(t: Tree, level: int) -> bool:
    c = t.children[0]
    return isinstance(c, Heading) and c.level == level


def is_heading(level: int) -> Callable[[Tree], bool]:
    """判定."""
    return functools.partial(_is_heading, level=level)


class Heading(BaseModel, frozen=True):
    """見出しまたは章節."""

    title: str
    level: int = Field(ge=1, le=6)

    def __str__(self) -> str:
        """For user string."""
        return f"h{self.level}={self.title}"


class TSource(Transformer):
    """source transformer."""

    def AUTHOR(self, tok: Token) -> str:  # noqa: N802
        """情報源の著者."""
        return tok.replace("author", "").strip()

    def PUBLISHED(self, tok: Token) -> str:  # noqa: N802
        """Markdown H1."""
        return tok.replace("published", "").strip()


class THeading(Transformer):
    """heading transformer."""

    def _common(self, tok: Token, level: int) -> Heading:
        v = tok.replace("#", "").strip()
        return Heading(title=v, level=level)

    def H1(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H1."""
        return self._common(tok, 1)

    def H2(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H2."""
        return self._common(tok, 2)

    def H3(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H3."""
        return self._common(tok, 3)

    def H4(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H4."""
        return self._common(tok, 4)

    def H5(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H5."""
        return self._common(tok, 5)

    def H6(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H6."""
        return self._common(tok, 6)

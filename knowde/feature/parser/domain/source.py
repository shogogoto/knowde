"""情報源ツリー."""
from __future__ import annotations

from datetime import date, datetime

from lark import Token, Transformer, Tree
from lark.visitors import Interpreter
from pydantic import BaseModel, Field

from knowde.core.timeutil import TZ
from knowde.feature.parser.domain.domain import Heading, SourceInfo


class TSource(Transformer):
    """source transformer."""

    def AUTHOR(self, tok: Token) -> str:  # noqa: N802
        """情報源の著者."""
        return tok.replace("@author", "").strip()

    def PUBLISHED(self, tok: Token) -> date:  # noqa: N802
        """Markdown H1."""
        v = tok.replace("@published", "").strip()
        return datetime.strptime(v, "%Y-%m-%d").astimezone(TZ)


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


class SourceNotFoundError(Exception):
    """ソースが見つからない."""


class SourceVisitor(Interpreter, BaseModel):
    """構文木から情報源の情報を取り出す."""

    infos: list[SourceInfo] = Field(default_factory=list)

    def h1(self, t: Tree) -> None:  # noqa: D102
        h: Heading = t.children[0]
        info = list(t.find_data("source_info"))
        if len(info) == 0:
            s = SourceInfo(title=h.title)
        else:
            author, published = info[0].children
            s = SourceInfo(
                title=h.title,
                author=author,
                published=published,
            )
        self.infos.append(s)

    def get(self, title: str) -> SourceInfo:  # noqa: D102
        ls = [s for s in self.infos if s.contains(title)]
        if len(ls) == 1:
            return ls[0]
        raise SourceNotFoundError

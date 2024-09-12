"""言明 syntax."""
from __future__ import annotations

from datetime import date, datetime
from functools import reduce
from typing import TYPE_CHECKING

from lark import Token, Transformer

from knowde.core.timeutil import TZ
from knowde.feature.parser.domain.domain import Comment, Heading

if TYPE_CHECKING:
    from lark.visitors import TransformerChain


def common_transformer() -> TransformerChain:
    """パースに使用するTransformer一式."""
    return THeading() * TSource() * TStatemet()


class TStatemet(Transformer):
    """statement transformer."""

    # def ALIAS(self, tok: Token) -> str:
    #     return tok

    def COMMENT(self, tok: Token) -> Comment:  # noqa: N802 D102
        v = tok.replace("!", "").strip()
        return Comment(value=v)

    def ONELINE(self, tok: Token) -> str:  # noqa: N802 D102
        v = tok.replace("\n", "").strip()
        return Token(type="ONELINE", value=v)

    def MULTILINE(self, tok: Token) -> str:  # noqa: N802 D102
        vs = tok.split("\\\n")
        v = reduce(lambda x, y: x + y.lstrip(), vs).replace("\n", "")
        return Token(type="MULTILINE", value=v)

    # def _NL(self, tok: Token) -> _DiscardType:
    #     print("#" * 80)
    #     print(tok)
    #     return Discard


class TSource(Transformer):
    """source transformer."""

    def AUTHOR(self, tok: Token) -> str:  # noqa: N802
        """情報源の著者."""
        return tok.replace("@author", "").strip()

    def PUBLISHED(self, tok: Token) -> date:  # noqa: N802
        """Markdown H1."""
        v = tok.replace("@published", "").strip()
        return datetime.strptime(v, "%Y-%m-%d").astimezone(TZ).date()


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

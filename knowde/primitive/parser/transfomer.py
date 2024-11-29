"""Tree Leaf変換=Tranformerと変換後型."""

from datetime import date, datetime
from functools import reduce

from lark import Token, Transformer
from lark.visitors import TransformerChain

from knowde.core.timeutil import TZ
from knowde.primitive.parser.leaf import Comment, ContextType, Heading


def common_transformer() -> TransformerChain:
    """パースに使用するTransformer一式."""
    return THeading() * TSourceAbout() * TStatemet() * TContext()


class TSourceAbout(Transformer):
    """source about transformer."""

    def AUTHOR(self, tok: Token) -> str:  # noqa: N802
        """情報源の著者."""
        return tok.replace("@author", "").strip()

    def PUBLISHED(self, tok: Token) -> date:  # noqa: N802
        """Markdown H1."""
        v = tok.replace("@published", "").strip()
        return datetime.strptime(v, "%Y-%m-%d").astimezone(TZ).date()


class TContext(Transformer):
    """context transformer."""

    def THUS(self, _tok: Token) -> ContextType:  # noqa: N802
        """故に. 言明の帰結."""
        return ContextType.THUS

    def CAUSE(self, _tok: Token) -> ContextType:  # noqa: N802
        """なぜなら。言明の前提."""
        return ContextType.CAUSE

    def ANTONYM(self, _tok: Token) -> ContextType:  # noqa: N802
        """対義語。言明の反対の意味."""
        return ContextType.ANTONYM

    def EXAMPLE(self, _tok: Token) -> ContextType:  # noqa: N802
        """例."""
        return ContextType.EXAMPLE

    def GENERAL(self, _tok: Token) -> ContextType:  # noqa: N802
        """一般化."""
        return ContextType.GENERAL

    def REF(self, _tok: Token) -> ContextType:  # noqa: N802
        """参考元."""
        return ContextType.REF

    def NUM(self, _tok: Token) -> ContextType:  # noqa: N802
        """リスト構成要素."""
        return ContextType.NUM

    def SIMILAR(self, _tok: Token) -> ContextType:  # noqa: N802
        """類似."""
        return ContextType.SIMILAR

    def WHEN(self, _tok: Token) -> ContextType:  # noqa: N802
        """いつ."""
        return ContextType.WHEN

    def BY(self, _tok: Token) -> ContextType:  # noqa: N802
        """アクター."""
        return ContextType.BY

    def EQUIV(self, _tok: Token) -> ContextType:  # noqa: N802
        """同値."""
        return ContextType.EQUIV


class TStatemet(Transformer):
    """statement transformer."""

    def _replace_value(self, tok: Token, v: str) -> str:
        return Token(type=tok.type, value=v)

    def COMMENT(self, tok: Token) -> Comment:  # noqa: N802 D102
        v = tok.replace("!", "").strip()
        return Comment(value=v)

    def ONELINE(self, tok: Token) -> str:  # noqa: N802 D102
        v = tok.replace("\n", "").strip()
        return self._replace_value(tok, v)

    def MULTILINE(self, tok: Token) -> str:  # noqa: N802 D102
        vs = tok.split("\\\n")
        v = reduce(lambda x, y: x + y.lstrip(), vs).replace("\n", "")
        return self._replace_value(tok, v)

    def ALIAS(self, tok: Token) -> str:  # noqa: D102 N802
        v = tok.replace("|", "").strip()
        return self._replace_value(tok, v)


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

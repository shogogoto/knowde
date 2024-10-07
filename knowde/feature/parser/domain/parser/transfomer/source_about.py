"""情報源について."""
from datetime import date, datetime

from lark import Token, Transformer

from knowde.core.timeutil import TZ


class TSourceAbout(Transformer):
    """source about transformer."""

    def AUTHOR(self, tok: Token) -> str:  # noqa: N802
        """情報源の著者."""
        return tok.replace("@author", "").strip()

    def PUBLISHED(self, tok: Token) -> date:  # noqa: N802
        """Markdown H1."""
        v = tok.replace("@published", "").strip()
        return datetime.strptime(v, "%Y-%m-%d").astimezone(TZ).date()

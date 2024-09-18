"""見出し."""
from lark import Token, Transformer
from pydantic import BaseModel, Field


class Heading(BaseModel, frozen=True):
    """見出しまたは章節."""

    title: str
    level: int = Field(ge=1, le=6)

    def __str__(self) -> str:
        """For user string."""
        return f"h{self.level}={self.title}"

    def contains(self, title: str) -> bool:
        """タイトルを含んでいるか."""
        return title in self.title


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

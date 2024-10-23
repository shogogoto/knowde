"""statement transformer."""
from functools import reduce

from lark import Token, Transformer
from pydantic import BaseModel


class Comment(BaseModel, frozen=True):
    """コメント."""

    value: str

    def __str__(self) -> str:
        """For user string."""
        return f"!{self.value}"


def _replace_value(tok: Token, v: str) -> str:
    return Token(type=tok.type, value=v)


class TStatemet(Transformer):
    """statement transformer."""

    def COMMENT(self, tok: Token) -> Comment:  # noqa: N802 D102
        v = tok.replace("!", "").strip()
        return Comment(value=v)

    def ONELINE(self, tok: Token) -> str:  # noqa: N802 D102
        v = tok.replace("\n", "").strip()
        return _replace_value(tok, v)

    def MULTILINE(self, tok: Token) -> str:  # noqa: N802 D102
        vs = tok.split("\\\n")
        v = reduce(lambda x, y: x + y.lstrip(), vs).replace("\n", "")
        return _replace_value(tok, v)

    def ALIAS(self, tok: Token) -> str:  # noqa: D102 N802
        v = tok.replace("|", "").strip()
        return _replace_value(tok, v)

    def NAME(self, tok: Token) -> str:  # noqa: D102 N802
        v = tok.replace("|", "").strip()
        return _replace_value(tok, v)

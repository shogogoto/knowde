"""言明 syntax."""
from functools import reduce

from lark import Token, Transformer
from pydantic import BaseModel


class Statement(BaseModel, frozen=True):
    """言明."""

    value: str


class Comment(BaseModel, frozen=True):
    """コメント."""

    value: str

    def __str__(self) -> str:
        """For user string."""
        return f"!{self.value}"


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

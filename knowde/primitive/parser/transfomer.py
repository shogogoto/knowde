"""Tree Leaf変換=Tranformerと変換後型."""
from __future__ import annotations

from typing import TYPE_CHECKING

from lark import Token, Transformer
from pydantic import BaseModel

from knowde.primitive.parser.lineparse import parse_line

if TYPE_CHECKING:
    from lark.visitors import TransformerChain


def common_transformer() -> TransformerChain | Transformer:
    """パースに使用するTransformer一式."""
    return TStatemet()


class Statement(BaseModel):
    """変換後行."""

    alias: str | None
    names: list[str]
    sentence: str | None


class TStatemet(Transformer):
    """statement transformer."""

    def ONELINE(self, tok: Token) -> Statement:  # noqa: N802 D102
        v = "".join(tok.split())
        alias, names, sentence = parse_line(v)
        return Statement(alias=alias, names=names, sentence=sentence)

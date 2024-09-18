"""about context."""
from __future__ import annotations

from enum import Enum, auto

from lark import Token, Transformer


class ContextType(Enum):
    """文脈の種類."""

    THUS = auto()
    CAUSE = auto()
    ANTONYM = auto()
    EXAMPLE = auto()
    GENERAL = auto()
    REF = auto()
    NUM = auto()


class TContext(Transformer):
    """context transformer."""

    def THUS(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.THUS

    def CAUSE(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.CAUSE

    def ANTONYM(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.ANTONYM

    def EXAMPLE(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.EXAMPLE

    def GENERAL(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.GENERAL

    def REF(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.REF

    def NUM(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.NUM

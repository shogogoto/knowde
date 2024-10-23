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
    SIMILAR = auto()
    WHEN = auto()
    BY = auto()
    EQUIV = auto()


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

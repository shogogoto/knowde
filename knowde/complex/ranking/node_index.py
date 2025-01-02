"""ランキング指標.

**一覧性のために!!!!!!!!!!!**
    検索とは異なる g -> list s with index
文の重要度のためにどういう統計値が欲しいのか
詳細の量 -> sibsの数
-> 引用される量
文の分類をまず考えるか 構造が見えてくる
    1階関係
    中心となる文とその文脈を与える文 EdgeType succ/pred で自然と分類されるか
    BELOW + SIBLING  /片方だけでは意味がない複合関係
        description / parent
    RESOLVED # s1 -[RESOLVED]-> s2 s2が依存されていて、中心に近い
        refer / referred
    TO
        conclusion / premise
多階層
    axioms
    leaves
"""

# 1階の周辺情報
from __future__ import annotations

from functools import cache
from typing import Generic, Self, TypeVar

from pydantic import BaseModel
from typing_extensions import override

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg
from knowde.primitive.__core__.nxutil import EdgeType, to_nodes

T = TypeVar("T")


class RankIndex(BaseModel, Generic[T], frozen=True):
    """ノードの重要度の指標."""

    values: list[T]
    prefix: str = ""
    n_display: int = -1
    scale: int = 1

    @classmethod
    @cache
    def create(cls, sn: SysNet, s: str, scale: int = 1, n_display: int = -1) -> Self:
        """Create method."""
        return cls(
            values=cls._create(sn, s),
            scale=scale,
            n_display=n_display,
        )

    @classmethod
    def _create(cls, sn: SysNet, s: str) -> list[T]:
        raise NotImplementedError

    def __str__(self) -> str:
        """Display for user."""
        return self._display()

    def _display(self) -> str:
        vals = self.values[: self.n_display]
        if self.n_display == -1:
            vals = self.values
        return f"{self.prefix}{vals}"

    def index(self) -> int:
        """指標."""
        return len(self.values) * self.scale


class Description(RankIndex[list[SysArg]], frozen=True):
    """詳細な記述."""

    prefix: str = "Desc"

    @classmethod
    def _create(cls, sn: SysNet, s: str) -> list:
        vals = []
        for below_s in EdgeType.BELOW.succ(sn.g, s):
            sibs = to_nodes(sn.g, below_s, EdgeType.SIBLING.succ)
            vals.append([sn.get(n) for n in sibs if n])  # None排除
        return vals

    @override
    def index(self) -> int:
        c = 0
        for ls in self.values:
            c += len(ls)
        return c


class Refer(RankIndex[SysArg], frozen=True):
    """引用・利用する側."""

    prefix: str = "rf"

    @classmethod
    def _create(cls, sn: SysNet, s: str) -> list:
        vals = list(EdgeType.RESOLVED.succ(sn.g, s))
        return list(map(sn.get, vals))


class Referred(RankIndex[SysArg], frozen=True):
    """引用される依存元."""

    prefix: str = "dep"

    @classmethod
    def _create(cls, sn: SysNet, s: str) -> list:
        vals = list(EdgeType.RESOLVED.pred(sn.g, s))
        return list(map(sn.get, vals))

    def _display(self) -> str:
        return f"rd{self.values}"


class Premise(RankIndex[SysArg], frozen=True):
    """前提."""

    prefix: str = "Pre"

    @classmethod
    def _create(cls, sn: SysNet, s: str) -> list:
        vals = list(EdgeType.TO.pred(sn.g, s))
        return list(map(sn.get, vals))

    def _display(self) -> str:
        return f"Pre{self.values}"


class Conclusion(RankIndex[SysArg], frozen=True):
    """前提."""

    prefix: str = "C"

    @classmethod
    def _create(cls, sn: SysNet, s: str) -> list:
        vals = list(EdgeType.TO.succ(sn.g, s))
        return list(map(sn.get, vals))

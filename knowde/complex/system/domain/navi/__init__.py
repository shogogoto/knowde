"""ナビ 任意sysnodeの位置を把握する羅針盤."""
from __future__ import annotations

from itertools import zip_longest
from typing import TYPE_CHECKING, Hashable, OrderedDict, Self

from pydantic import BaseModel

from knowde.complex.system.domain.nxutil import axiom_paths, leaf_paths
from knowde.complex.system.domain.sysnet import EdgeType, SysNet
from knowde.complex.system.domain.sysnet.sysnode import SysNode

if TYPE_CHECKING:
    from networkx import DiGraph


class Navi(BaseModel, frozen=True):
    """現在位置."""

    node: Hashable
    axiom_paths: list[list[Hashable]]
    leaf_paths: list[list[Hashable]]
    t: EdgeType

    @classmethod
    def create(cls, g: DiGraph, n: SysNode, t: EdgeType) -> Self:
        """ファクトリー."""
        return cls(
            node=n,
            axiom_paths=axiom_paths(g, n, t),
            leaf_paths=leaf_paths(g, n, t),
            t=t,
        )

    @property
    def max_pred_depth(self) -> int:
        """最大前距離."""
        return max([len(p) for p in self.axiom_paths])

    @property
    def max_succ_depth(self) -> int:
        """最大次距離."""
        return max([len(p) for p in self.leaf_paths])

    def succs(self, depth: int) -> list(Hashable):
        """depth先のnodesを取得."""
        return verticallist2d(self.leaf_paths, depth)

    def preds(self, depth: int) -> list(Hashable):
        """depth前のnodesを取得."""
        return verticallist2d(self.axiom_paths, depth)


def verticallist2d(ls2d: list[list[Hashable]], depth: int) -> list[Hashable]:
    """2次元リストから列を取得."""
    ls = list(zip_longest(*ls2d, fillvalue=None))
    try:
        ls = list(OrderedDict.fromkeys(ls[depth]).keys())
        return [e for e in ls if e is not None]
    except IndexError:
        return []


class Explorer(BaseModel):
    """ネットワーク上を移動."""

    current: Navi
    sn: SysNet

    def succ(self, t: EdgeType, i: int) -> None:
        """先へ移動."""
        self.current.succs[i]

    def pred(self, t: EdgeType, i: int) -> None:
        """前へ移動."""
        self.current.preds[i]

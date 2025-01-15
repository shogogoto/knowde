"""ネットワーク1 node1のview."""
from __future__ import annotations

from enum import Enum, StrEnum
from functools import cached_property
from typing import NamedTuple, Self

from more_itertools import collapse
from pydantic import BaseModel, Field
from tabulate import tabulate

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg, SysNode
from knowde.complex.systats.nw1_n1 import (
    Nw1N1Fn,
    get_conclusion,
    get_detail,
    get_premise,
    get_refer,
    get_referred,
    recursively_nw1n1,
)


class SysCtxItem(StrEnum):
    """文脈タイプ."""

    DETAIL = "detail"
    REFER = "refer"
    REFERRED = "referred"
    PREMISE = "premise"
    CONCLUSION = "conclusion"


class SysContext(Enum):
    """文脈."""

    DETAIL = (SysCtxItem.DETAIL, get_detail)
    REFER = (SysCtxItem.REFER, get_refer)
    REFERRED = (SysCtxItem.REFERRED, get_referred)
    PREMISE = (SysCtxItem.PREMISE, get_premise)
    CONCLUSION = (SysCtxItem.CONCLUSION, get_conclusion)

    item: SysCtxItem
    fn: Nw1N1Fn

    def __init__(self, item: SysCtxItem, fn: Nw1N1Fn) -> None:
        """For merge."""
        self.item = item
        self.fn = fn

    @classmethod
    def from_item(cls, item: SysCtxItem) -> Self:
        """Create from item."""
        for e in cls:
            if e.item == item:
                return e
        raise ValueError(item)

    def __call__(
        self,
        sn: SysNet,
        n: SysNode,
        count: int,
        weight: int,
    ) -> SysCtxReturn:
        """Return for viewing."""
        rec_f = recursively_nw1n1(self.fn, count)
        return SysCtxReturn(name=self.item, ls=rec_f(sn, n), weight=weight)


class SysCtxReturn(BaseModel, frozen=True):
    """SysContextの返り値."""

    name: SysCtxItem
    ls: list
    weight: int

    @cached_property
    def count(self) -> int:
        """総数."""
        return len(list(collapse(self.ls, base_type=BaseModel)))

    @property
    def score(self) -> int:
        """重み付き."""
        return self.count * self.weight


class SysCtxView(BaseModel, frozen=True):
    """SysCtxReturnのまとめ."""

    n: SysArg
    rets: list[SysCtxReturn]

    def __lt__(self, other: Self) -> bool:  # noqa: D105
        return self.index < other.index

    def to_dict(self) -> dict:
        """To dict for tabulate view."""
        d = {r.name: r.count for r in self.rets}
        d["score"] = self.index
        d["sentence"] = self.n
        return d

    def __len__(self) -> int:  # noqa: D105
        return len(self.rets)

    @cached_property
    def index(self) -> int:
        """For sorting."""
        return sum([r.score for r in self.rets])


"""
どの項目を表示するか
rec指定
数値ではなくリストで表示
表示行数指定

n_rec, weight, listview or numview
"""


class RecWeight(NamedTuple):
    """再帰回数と重みの設定."""

    item: SysCtxItem
    n_rec: int
    weight: int

    def get_tuple(self) -> tuple[int, int]:  # noqa: D102
        return self.n_rec, self.weight


class SysContexts(BaseModel, frozen=True):
    """コレクション."""

    values: list[SysContext]
    num: int = Field(title="表示行数")
    configs: list[RecWeight]

    def __call__(self, sn: SysNet) -> list[SysCtxView]:
        """コレクションをまとめて適用して返す."""
        ls = []
        for s in sn.sentences:
            view = SysCtxView(
                n=sn.get(s),
                rets=[v(sn, s, *self._rec_weight(v.item)) for v in self.values],
            )
            ls.append(view)
        ls = sorted(ls, reverse=True)
        return ls[: self.num]

    def table(self, sn: SysNet) -> str:
        """table表示."""
        return tabulate([e.to_dict() for e in self(sn)], headers="keys")

    def _rec_weight(self, v: SysCtxItem) -> tuple[int, int]:
        for c in self.configs:
            if c.item == v:
                return c.get_tuple()
        return (1, 1)

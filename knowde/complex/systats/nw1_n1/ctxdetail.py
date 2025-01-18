"""nw1n1の周辺情報というか文脈詳細というか."""
from __future__ import annotations

from enum import Enum, StrEnum
from typing import Iterable, NamedTuple, Self

from pydantic import BaseModel

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysNode
from knowde.complex.systats.nw1_n1 import (
    Nw1N1Fn,
    get_conclusion,
    get_detail,
    get_premise,
    get_refer,
    get_referred,
    recursively_nw1n1,
)


class Nw1N1Label(StrEnum):
    """文脈タイプ."""

    DETAIL = "detail"
    REFER = "refer"
    REFERRED = "referred"
    PREMISE = "premise"
    CONCLUSION = "conclusion"


class Nw1N1Ctx(Enum):
    """1nw1n文脈."""

    DETAIL = (Nw1N1Label.DETAIL, get_detail)
    REFER = (Nw1N1Label.REFER, get_refer)
    REFERRED = (Nw1N1Label.REFERRED, get_referred)
    PREMISE = (Nw1N1Label.PREMISE, get_premise)
    CONCLUSION = (Nw1N1Label.CONCLUSION, get_conclusion)

    label: Nw1N1Label
    fn: Nw1N1Fn

    def __init__(self, label: Nw1N1Label, fn: Nw1N1Fn) -> None:
        """For merge."""
        self.label = label
        self.fn = fn

    @classmethod
    def from_label(cls, label: Nw1N1Label) -> Self:
        """Create from label."""
        for e in cls:
            if e.label == label:
                return e
        raise ValueError(label)


class Nw1N1Recursive(NamedTuple):
    """どのlabelで何回再帰的に返すか."""

    label: Nw1N1Label
    n_rec: int


class Nw1N1Detail(BaseModel, frozen=True):
    """1nw 1nodeの詳細."""

    values: list[Nw1N1Ctx]
    recs: Iterable[Nw1N1Recursive]

    def __call__(self, sn: SysNet, n: SysNode) -> dict:
        """Aaaa."""
        d = {}
        for v in self.values:
            n_rec = self._get_n_rec(v.label)
            fn = recursively_nw1n1(v.fn, n_rec)
            d[v.label.value] = fn(sn, n)
        return d

    def _get_n_rec(self, lb: Nw1N1Label) -> int:
        match = [r for r in self.recs if r.label == lb]
        if len(match) == 0:
            return 1
        return match[0].n_rec

    @classmethod
    def create(
        cls,
        targets: Iterable[Nw1N1Label] = [],
        ignores: Iterable[Nw1N1Label] = [],
        recs: Iterable[Nw1N1Recursive] = [],
    ) -> Self:
        """instantiate."""
        return cls(
            values=[Nw1N1Ctx.from_label(i) for i in targets if i not in ignores],
            recs=recs,
        )

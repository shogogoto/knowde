"""nw1n1の周辺情報というか文脈詳細というか."""

from __future__ import annotations

import textwrap
from collections.abc import Callable, Iterable
from enum import Enum
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel

from knowde.feature.systats.nw1_n1 import (
    Nw1N1Fn,
    get_conclusion,
    get_detail,
    get_example,
    get_general,
    get_premise,
    get_refer,
    get_referred,
    recursively_nw1n1,
)
from knowde.feature.systats.types import Nw1N1Label, Nw1N1Recursive

if TYPE_CHECKING:
    from knowde.feature.parsing.sysnet import SysNet
    from knowde.feature.parsing.sysnet.sysnode import KNArg
    from knowde.shared.types import Duplicable


class Nw1N1Ctx(Enum):
    """1nw1n文脈."""

    DETAIL = (Nw1N1Label.DETAIL, get_detail, "")
    REFER = (Nw1N1Label.REFER, get_refer, ">>")
    REFERRED = (Nw1N1Label.REFERRED, get_referred, "<<")
    PREMISE = (Nw1N1Label.PREMISE, get_premise, "<-")
    CONCLUSION = (Nw1N1Label.CONCLUSION, get_conclusion, "->")
    EXAMPLE = (Nw1N1Label.EXAMPLE, get_example, "ex.")
    GENERAL = (Nw1N1Label.GENERAL, get_general, "xe.")

    label: Nw1N1Label
    fn: Nw1N1Fn
    prefix: str

    def __init__(self, label: Nw1N1Label, fn: Nw1N1Fn, prefix: str) -> None:
        """For merge."""
        self.label = label
        self.fn = fn
        self.prefix = prefix

    @classmethod
    def from_label(cls, label: Nw1N1Label) -> Self:
        """Create from label."""
        for e in cls:
            if e.label == label:
                return e
        raise ValueError(label)

    def format(self, n: KNArg) -> str:
        """整形."""
        return f"{self.prefix} {n}"


def apply_nest(nest: list, func: Callable) -> list:
    """入れ子リストに関数を適用."""
    res = []
    for item in nest:
        if isinstance(item, list):
            res.append(apply_nest(item, func))
        else:
            res.append(func(item))
    return res


class Nw1N1Detail(BaseModel, frozen=True):
    """1nw 1nodeの詳細."""

    values: list[Nw1N1Ctx]
    recs: Iterable[Nw1N1Recursive]

    def ctx_dict(self, sn: SysNet, n: str | Duplicable) -> dict[Nw1N1Label, list]:
        """Aaaa."""
        d = {}
        for v in self.values:
            n_rec = self._get_n_rec(v.label)
            fn = recursively_nw1n1(v.fn, n_rec)
            d[v.label.value] = apply_nest(fn(sn, n), sn.expand)
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
        """Instantiate."""
        return cls(
            values=[Nw1N1Ctx.from_label(i) for i in targets if i not in ignores],
            recs=recs,
        )

    def format(self, sn: SysNet, n: str | Duplicable) -> str:
        """整形文字列."""
        txt = f"{sn.expand(n)}\n"
        d = self.ctx_dict(sn, n)
        for k, v in d.items():
            fmt = Nw1N1Ctx.from_label(k).format
            content = to_indented_str(apply_nest(v, fmt))
            if len(content) == 0:
                continue
            txt += textwrap.indent(content, "  ")
        return txt


def to_indented_str(nested: list, length: int = 2, level: int = 0) -> str:
    """インデント付き文字列."""
    result = ""
    indent = " " * length * level
    for item in nested:
        if isinstance(item, list):
            result += to_indented_str(item, length, level + 1)
        else:
            result += indent + item + "\n"
    return result

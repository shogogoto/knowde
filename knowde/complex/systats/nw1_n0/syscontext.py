"""ネットワーク1 node1のview."""
from __future__ import annotations

from functools import cached_property
from typing import Iterable, NamedTuple, Self, Sequence

from more_itertools import collapse
from pydantic import BaseModel, Field

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg, SysNode
from knowde.complex.systats.nw1_n1 import recursively_nw1n1
from knowde.complex.systats.nw1_n1.ctxdetail import Nw1N1Label, SysContext


class RecursiveWeight(NamedTuple):
    """再帰回数と重みの設定."""

    label: Nw1N1Label
    n_rec: int
    weight: int


class CtxScorable(BaseModel, frozen=True):
    """scoreを返す."""

    label: Nw1N1Label
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

    @classmethod
    def create(cls, sn: SysNet, n: SysNode, rw: RecursiveWeight) -> Self:
        """Instantiate."""
        ctx = SysContext.from_label(rw.label)
        rec_f = recursively_nw1n1(ctx.fn, rw.n_rec)
        return cls(label=rw.label, ls=rec_f(sn, n), weight=rw.weight)


class CtxScorables(BaseModel, frozen=True):
    """CtxScorebleのまとめ."""

    n: SysArg
    rets: list[CtxScorable]

    def __lt__(self, other: Self) -> bool:  # noqa: D105
        return self.index < other.index

    def to_dict(self) -> dict:
        """To dict for tabulate view."""
        d = {r.label: r.count for r in self.rets}
        d["score"] = self.index
        d["sentence"] = self.n
        return d

    def __len__(self) -> int:  # noqa: D105
        return len(self.rets)

    @cached_property
    def index(self) -> int:
        """For sorting."""
        return sum([r.score for r in self.rets])


class CtxConfig(BaseModel, frozen=True):
    """再帰回数と重み設定."""

    configs: Iterable[RecursiveWeight]

    def _rw(self, v: Nw1N1Label) -> RecursiveWeight:
        for c in self.configs:
            if c.label == v:
                return c
        return RecursiveWeight(v, 1, 1)

    def __call__(self, sn: SysNet, n: SysNode, ctxs: list[SysContext]) -> CtxScorables:
        """再帰重み付き."""
        return CtxScorables(
            n=sn.get(n),
            rets=[CtxScorable.create(sn, n, self._rw(c.label)) for c in ctxs],
        )


class SysContexts(BaseModel, frozen=True):
    """コレクション."""

    values: list[SysContext]
    config: CtxConfig = Field(default_factory=lambda _: CtxConfig(configs=[]))

    @classmethod
    def create(
        cls,
        targets: Iterable[Nw1N1Label] = [],
        ignores: Iterable[Nw1N1Label] = [],
        config: Iterable[RecursiveWeight] = [],
    ) -> Self:
        """instantiate."""
        return cls(
            values=[SysContext.from_label(i) for i in targets if i not in ignores],
            config=CtxConfig(configs=config),
        )

    def __call__(self, sn: SysNet, ns: Sequence[SysNode]) -> list[CtxScorables]:
        """コレクションをまとめて適用して返す."""
        if len(ns) == 0:
            ns = sn.sentences
        ls = []
        for s in ns:
            rets = self.config(sn, s, self.values)
            ls.append(rets)
        return sorted(ls, reverse=True)

    def to_json(
        self,
        sn: SysNet,
        ns: Sequence[SysNode] = [],
        num: int = 50,
    ) -> list[dict]:
        """Table or json表示用."""
        return [e.to_dict() for e in self(sn, ns)[:num]]

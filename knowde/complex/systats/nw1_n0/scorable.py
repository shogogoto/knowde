"""ネットワーク1 node1のview."""
from __future__ import annotations

from typing import Iterable, NamedTuple, Self, Sequence

from more_itertools import collapse
from pydantic import BaseModel, Field

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import (
    SysArg,
    SysNode,
)
from knowde.complex.systats.nw1_n1 import recursively_nw1n1
from knowde.complex.systats.nw1_n1.ctxdetail import Nw1N1Ctx, Nw1N1Label


class LRWTpl(NamedTuple):
    """再帰回数と重みの設定."""

    label: Nw1N1Label
    n_rec: int
    weight: int


class CtxScorable(BaseModel, frozen=True):
    """scoreを返す."""

    label: Nw1N1Label
    ls: list
    weight: int

    @property
    def count(self) -> int:
        """総数."""
        return len(list(collapse(self.ls, base_type=BaseModel)))

    @property
    def score(self) -> int:
        """重み付き."""
        return self.count * self.weight

    @classmethod
    def create(cls, sn: SysNet, n: SysNode, rw: LRWTpl) -> Self:
        """Instantiate."""
        sn.check_contains(n)
        ctx = Nw1N1Ctx.from_label(rw.label)
        rec_f = recursively_nw1n1(ctx.fn, rw.n_rec)
        return cls(label=rw.label, ls=rec_f(sn, n), weight=rw.weight)


class CtxScorables(BaseModel, frozen=True):
    """CtxScorebleのまとめ."""

    n: SysArg
    rets: list[CtxScorable]

    def __lt__(self, other: Self) -> bool:  # noqa: D105
        return self.score < other.score

    def to_dict(self, _sn: SysNet) -> dict:
        """To dict for tabulate view."""
        d = self.get()
        d["sentence"] = self.n
        return d

    def __len__(self) -> int:  # noqa: D105
        return len(self.rets)

    @property
    def score(self) -> int:
        """For sorting."""
        return sum([r.score for r in self.rets])

    def get(self) -> dict:
        """Get dict."""
        d = {r.label.value: r.count for r in self.rets}
        d["score"] = self.score
        return d


class CtxConfig(BaseModel, frozen=True):
    """再帰回数と重み設定."""

    configs: list[LRWTpl]

    def _tpl(self, v: Nw1N1Label) -> LRWTpl:
        for c in self.configs:
            if c.label == v:
                return c
        return LRWTpl(v, 1, 1)

    def get(self, sn: SysNet, n: SysNode, ctxs: list[Nw1N1Ctx]) -> CtxScorables:
        """再帰重み付き."""
        return CtxScorables(
            n=n,  # collapse scoreに影響
            rets=[CtxScorable.create(sn, n, self._tpl(c.label)) for c in ctxs],
        )


class SysContexts(BaseModel, frozen=True):
    """コレクション."""

    values: list[Nw1N1Ctx]
    config: CtxConfig = Field(default_factory=lambda _: CtxConfig(configs=[]))

    @classmethod
    def create(
        cls,
        targets: Iterable[Nw1N1Label] = [],
        ignores: Iterable[Nw1N1Label] = [],
        config: Iterable[LRWTpl] = [],
    ) -> Self:
        """instantiate."""
        return cls(
            values=[Nw1N1Ctx.from_label(i) for i in targets if i not in ignores],
            config=CtxConfig(configs=config),
        )

    def sort(self, sn: SysNet, ns: Sequence[SysNode] = []) -> list[CtxScorables]:
        """コレクションをまとめて適用して返す."""
        if len(ns) == 0:
            ns = sn.sentences
        ls = []
        for s in ns:
            rets = self.config.get(sn, s, self.values)
            ls.append(rets)
        return sorted(ls, reverse=True)

    def to_json(
        self,
        sn: SysNet,
        ns: Sequence[SysNode] = [],
        num: int = 50,
    ) -> list[dict]:
        """Table or json表示用."""
        return [e.to_dict(sn) for e in self.sort(sn, ns)[:num]]

    def get_one(self, sn: SysNet, n: str) -> dict:
        """指定ノードのみ返す."""
        return self.config.get(sn, n, self.values).get()

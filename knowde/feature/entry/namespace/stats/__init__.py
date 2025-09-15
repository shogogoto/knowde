"""NW1 node0の値、統計値."""

from __future__ import annotations

import operator
from collections.abc import Callable
from enum import Enum, StrEnum
from functools import reduce
from typing import Self

import networkx as nx

from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.types import Duplicable

from .domain import (
    get_axiom,
    get_isolation,
    get_unrefered,
)

type NW1N0Fn = Callable[[SysNet], int]
type NW1N0RatioFn = Callable[[SysNet], float]


def n_char(sn: SysNet) -> int:  # noqa: D103
    c = 0
    for n in sn.g.nodes:
        match n:
            case str() | Duplicable():
                c += len(str(n))
            case Term():
                c += 0 if len(n.names) == 0 else reduce(operator.add, map(len, n.names))
                c += len(n.alias) if n.alias else 0
            case _:
                raise TypeError
    return c


class Nw1N0Label(StrEnum):
    """Nw1N0統計値ラベル."""

    # number
    EDGE = "edge"
    TERM = "term"
    SENTENCE = "sentence"
    CHAR = "char"
    ISOLATION = "isolation"
    AXIOM = "axiom"
    TERM_AXIOM = "term_axiom"
    # nx number
    DIAMETER = "diameter"
    RADIUS = "radius"

    # ratio
    R_ISOLATION = "isolation_ratio"
    R_AXIOM_TERM = "axiom_term_ratio"
    R_AXIOM = "axiom_ratio"
    # nx ratio
    R_DENSITY = "density"

    @classmethod
    def create(cls, label: Nw1N0Label) -> Systat | UnificationRatio:
        """Create from label."""
        for e in Systat:
            if e.label == label:
                return e
        for e in UnificationRatio:
            if e.label == label:
                return e
        raise ValueError(label)

    @classmethod
    def heavy(cls) -> list[Nw1N0Label]:
        """重いnetworkx処理."""
        return [
            cls.DIAMETER,
            cls.RADIUS,
            cls.R_DENSITY,
        ]

    @classmethod
    def standard(cls) -> list[Nw1N0Label]:
        """重くない統計値."""
        return [r for r in cls if r not in cls.heavy()]

    @classmethod
    def to_dict(cls, sn: SysNet, labels: list[Self]) -> dict:
        """全統計値."""
        nws = [cls.create(lb) for lb in labels]
        d = {}
        for nw in nws:
            dct = nw.to_dict(sn)
            if nw in UnificationRatio:
                dct = to_percent_values(dct)
            d |= dct
        return d


class Systat(Enum):
    """統計情報の構成要素."""

    EDGE = (Nw1N0Label.EDGE, lambda sn: len(sn.g.edges))
    TERM = (Nw1N0Label.TERM, lambda sn: len(sn.terms))
    SENTENCE = (Nw1N0Label.SENTENCE, lambda sn: len(sn.sentences))
    CHAR = (Nw1N0Label.CHAR, n_char)
    ISOLATION = (Nw1N0Label.ISOLATION, lambda sn: len(get_isolation(sn)))
    AXIOM = (Nw1N0Label.AXIOM, lambda sn: len(get_axiom(sn)))
    TERM_AXIOM = (Nw1N0Label.TERM_AXIOM, lambda sn: len(get_unrefered(sn)))
    # heavy
    DIAMETER = (Nw1N0Label.DIAMETER, lambda sn: nx.diameter(sn.g.to_undirected()))
    RADIUS = (Nw1N0Label.RADIUS, lambda sn: nx.radius(sn.g.to_undirected()))

    label: str
    fn: NW1N0Fn

    def __init__(self, label: str, fn: NW1N0Fn) -> None:
        """For merge."""
        self.label = label
        self.fn = fn

    def to_dict(self, sn: SysNet) -> dict[str, int]:
        """For json etc."""
        return {self.label: self.fn(sn)}


def ratio_fn(numerator: NW1N0Fn, denominator: NW1N0Fn) -> NW1N0RatioFn:
    """ゼロ割エラー回避."""

    def _fn(sn: SysNet) -> float:
        n = numerator(sn)
        d = denominator(sn)
        if d == 0:
            return float("inf")
        return n / d

    return _fn


class UnificationRatio(Enum):
    """1系の統合化(まとまり具体)指標."""

    ISOLATION = (
        Nw1N0Label.R_ISOLATION,
        ratio_fn(Systat.ISOLATION.fn, Systat.SENTENCE.fn),
    )
    TERM = (Nw1N0Label.R_AXIOM_TERM, ratio_fn(Systat.TERM_AXIOM.fn, Systat.TERM.fn))
    AXIOM = (Nw1N0Label.R_AXIOM, ratio_fn(Systat.AXIOM.fn, Systat.SENTENCE.fn))
    # heavy
    DENSITY = (Nw1N0Label.R_DENSITY, lambda sn: nx.density(sn.g))

    label: str
    fn: NW1N0RatioFn

    def __init__(self, label: str, fn: NW1N0RatioFn) -> None:
        """For merge."""
        self.label = label
        self.fn = lambda sn: round(fn(sn), 3)

    def to_dict(self, sn: SysNet) -> dict[str, float]:
        """For json etc."""
        return {self.label: self.fn(sn)}


def to_percent_values(d: dict[str, float], n_digit: int = 2) -> dict[str, str]:
    """パーセント表示."""
    return {k: f"{v:.{n_digit}%}" for k, v in d.items()}

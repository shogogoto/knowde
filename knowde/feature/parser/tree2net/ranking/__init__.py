"""指標でソート."""
from __future__ import annotations

import operator
from functools import cached_property, reduce

from pydantic import BaseModel

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg
from knowde.feature.parser.tree2net.ranking.node_index import (
    Conclusion,
    Description,
    Premise,
    RankIndex,
    Refer,
    Referred,
)


class Chunk(BaseModel, frozen=True):
    """周辺情報とindexを含んだビュー."""

    center: SysArg
    indexes: list[RankIndex]

    @cached_property
    def rank(self) -> int:
        """指標."""
        return reduce(operator.add, [i.index() for i in self.indexes])

    def __str__(self) -> str:  # noqa: D105
        return f"{self.center}"


def get_ranking(sn: SysNet) -> list[Chunk]:
    """1文がSysNetの中心."""
    index_types_with_weight = [
        (Description, 1),
        (Refer, 5),
        (Referred, 5),
        (Premise, 3),
        (Conclusion, 4),
    ]
    ls = []
    for s in sn.sentences:
        c = Chunk(
            center=sn.get(s),
            indexes=[
                it.create(sn, s, scale=scale) for it, scale in index_types_with_weight
            ],
        )
        ls.append(c)
    return sorted(ls, key=lambda x: x.rank)

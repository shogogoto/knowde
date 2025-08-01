"""adjacent 直近の周辺情報.

    as logic
      premises -> self
      conclusions <- self
    as term
      refer この文が引用する文 参照 -> self
      referred この文が引用している文 被参照 <- self
    as part
      detail
      parent.

DB 検索
term: sentでマッチ
その文脈を加える
"""

import itertools
from collections.abc import Hashable, Iterable
from uuid import UUID

from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.feature.entry.mapper import MResource
from knowde.feature.parsing.primitive.term import Term
from knowde.shared.nxutil import to_nodes
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import NXGraph
from knowde.shared.user.schema import UserReadPublic


class Additional(BaseModel, frozen=True):
    """knowde付加情報."""

    when: str | None = None
    where: str | None = None
    by: str | None = None


class KStats(BaseModel, frozen=True):
    """知識の関係統計."""

    # frontendのモック自動生成で数値の範囲を制限したい
    n_detail: int = Field(ge=-100, le=1000)
    n_premise: int = Field(ge=-100, le=1000)
    n_conclusion: int = Field(ge=-100, le=1000)
    n_refer: int = Field(ge=-100, le=1000)
    n_referred: int = Field(ge=-100, le=1000)
    dist_axiom: int = Field(ge=-100, le=1000)
    dist_leaf: int = Field(ge=-100, le=1000)
    score: int | None = Field(default=None, ge=-100, le=1000)

    def __str__(self) -> str:  # noqa: D105
        ls = [
            self.n_detail,
            self.n_premise,
            self.n_conclusion,
            self.n_refer,
            self.n_referred,
            self.dist_axiom,
            self.dist_leaf,
            self.score,
        ]
        return str(ls)


class Knowde(BaseModel, frozen=True):
    """知識の最小単位."""

    sentence: str
    uid: UUID
    term: Term | None = None
    additional: Additional | None = None
    stats: KStats
    resource_uid: UUID

    def __str__(self) -> str:  # noqa: D105
        a = self.additional
        t = f"[{self.term}]" if self.term else ""
        when = f"T({a.when})" if a is not None and a.when else ""
        return f"{self.sentence}{t}{when}"

    def when(self) -> str:  # noqa: D102
        a = self.additional
        return f"T({a.when})" if a is not None and a.when else ""


class ResourceOwnsers(BaseModel):
    """リソースの所有者."""

    user: UserReadPublic
    resource: MResource


class KnowdeSearchResult(BaseModel):
    """knowde検索結果."""

    total: int
    data: list[Knowde]
    owners: dict[UUID, ResourceOwnsers]


class UidStr(BaseModel):
    """UUID付き文章."""

    val: str
    uid: UUID


class LocationWithoutParents(BaseModel):
    """親なしknowdeの位置情報."""

    user: UserReadPublic
    folders: list[UidStr]
    resource: MResource
    headers: list[UidStr]

    # for debug
    def __str__(self) -> str:  # noqa: D105
        return f"{self.user.username} {'>'.join([h.val for h in self.headers])}"


class KnowdeLocation(LocationWithoutParents):
    """knowdeの位置情報."""

    parents: list[Knowde]


class KAdjacency(BaseModel):
    """周辺情報も含める."""

    center: Knowde
    details: list[Knowde]
    premises: list[Knowde]
    conclusions: list[Knowde]
    refers: list[Knowde]
    referreds: list[Knowde]

    def __str__(self) -> str:
        """For display in CLI."""
        s = str(self.center)
        s += f"@{self.center.when()}"
        s += "\n" + str(self.center.stats) if self.center.stats else ""
        if self.details:
            s += f"  {{ {', '.join(map(str, self.details))} }}"
        if self.premises:
            s += f"\n<- {', '.join(map(str, self.premises))}"
        if self.conclusions:
            s += f"\n-> {', '.join(map(str, self.conclusions))}"
        if self.refers:
            s += f"\n<< {', '.join(map(str, self.refers))}"
        if self.referreds:
            s += f"\n>> {', '.join(map(str, self.referreds))}"
        return s


class KnowdeDetail(BaseModel):
    """詳細."""

    uid: UUID
    g: NXGraph
    knowdes: dict[UUID, Knowde]
    location: KnowdeLocation

    # テスト用メソッド
    def get(self, sentence: str) -> UUID:  # noqa: D102
        for k, v in self.knowdes.items():
            if v.sentence == sentence:
                if v.uid.hex not in self.g:
                    raise ValueError
                return k
        raise ValueError

    def succ(self, sentence: str, t: EdgeType) -> list[Knowde]:  # noqa: D102
        uid = self.get(sentence)
        succs = list(t.succ(self.g, uid.hex))
        return [self.knowdes[UUID(s)] for s in succs]

    def part(self, tgt: str) -> set[Knowde]:
        """targetも含めて返す."""
        uid = self.get(tgt)

        is_first = True

        def succ(g: DiGraph, n: Hashable) -> Iterable[Hashable]:
            nonlocal is_first
            it = itertools.chain(
                EdgeType.BELOW.succ(g, n),
                EdgeType.SIBLING.succ(g, n) if not is_first else [],
            )
            is_first = False
            return it

        ns = to_nodes(self.g, uid.hex, succ)
        return {self.knowdes.get(UUID(s)) for s in ns if s is not None}

    @property
    def graph(self) -> DiGraph:  # noqa: D102
        g = DiGraph()

        for u, v, attr in self.g.edges(data=True):
            uu = self.knowdes.get(UUID(u))
            vv = self.knowdes.get(UUID(v))
            if uu is not None and vv is not None:
                g.add_edge(uu, vv, **attr)
        return g

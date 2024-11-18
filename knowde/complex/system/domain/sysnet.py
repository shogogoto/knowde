"""系ネットワーク."""
from __future__ import annotations

from enum import Enum, auto
from typing import Self, TypeAlias
from uuid import UUID, uuid4

from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.complex.system.domain.nxutil import succ_nested
from knowde.core.types import NXGraph

from .term.domain import Term


class EdgeType(Enum):
    """グラフ関係の種類."""

    HEAD = auto()  # 見出しを配下にする
    BELOW = auto()  # 配下 階層が下がる 直列
    SIBLING = auto()  # 兄弟 同階層 並列

    DEF = auto()  # term -> 文

    # 文と文
    TO = auto()  # 依存
    CONCRETE = auto()  # 具体
    WHEN = auto()
    # 両方向
    ANTI = auto()  # 反対


class Definition(BaseModel, frozen=True):
    """定義."""

    term: Term
    sentence: str

    @classmethod
    def create(cls, sentence: str, names: list[str], alias: str | None = None) -> Self:
        """便利コンストラクタ."""
        t = Term.create(*names, alias=alias)
        return cls(term=t, sentence=sentence)

    def __str__(self) -> str:  # noqa: D105
        return f"{self.term}: {self.sentence}"


SysNodeType: TypeAlias = Term | Definition | str


class Duplicable(BaseModel, frozen=True):
    """コメントや区分け文字列.

    区分け文字 みたいな区切りを作るためだけの無意味な文字列の扱いは?
    同一文字列は重複して登録できない.
    なので、uuidを付与する
    """

    n: str
    uid: UUID = Field(default_factory=uuid4)

    def __str__(self) -> str:  # noqa: D105
        return str(self.n)


class SysNetwork(BaseModel):
    """系ネットワーク."""

    root: str
    g: NXGraph = Field(default_factory=DiGraph, init=False)

    def nested(self) -> dict:  # noqa: D102
        return succ_nested(self.g, self.root)

    def head(self, pre: str, succ: str) -> None:
        """見出し追加."""
        self._ctx_to(pre, succ, EdgeType.HEAD)

    def below(self, pre: SysNodeType, succ: SysNodeType) -> None:
        """配下に追加."""
        self._ctx_to(pre, succ, EdgeType.BELOW)

    def sibling(self, pre: SysNodeType, succ: SysNodeType) -> None:
        """兄弟に追加."""
        self._ctx_to(pre, succ, EdgeType.SIBLING)

    def to(self, pre: str, succ: str) -> None:
        """推論関係."""
        self._ctx_to(pre, succ, EdgeType.TO)

    def _ctx_to(self, pre: SysNodeType, succ: SysNodeType, t: EdgeType) -> None:
        p = self._add(pre)
        succ_ = self._add(succ)
        self.g.add_edge(p, succ_, type=t)

    def _add(self, n: SysNodeType) -> str | Term:
        """定義の追加."""
        match n:
            case Term() | str():
                self.g.add_node(n)
                return n
            case Definition():
                self._ctx_to(n.term, n.sentence, EdgeType.DEF)
                return n.sentence
            case _:
                raise TypeError

    # head: str = Field(default="dummy", init=False)
    # ctx: SysNodeType | None = Field(default=None, init=False)
    # def model_post_init(self, __context: Any) -> None:
    #     self.head = self.root
    # def up(self, times: int = 1) -> None:
    #     """ctxを1つ上に上がる."""
    #     for _ in range(times):
    #         pres = list(self.g.predecessors(self.head))
    #         match len(pres):
    #             case 0:
    #                 pass
    #             case 1:
    #                 self.head = pres[0]
    #             case _:
    #                 raise UpContextError  # 常に親は１つだけ遡れる

"""系ネットワークのノード."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from typing import TYPE_CHECKING, Final, Self, override

from lark import Token
from pydantic import BaseModel

from knowde.feature.parsing.primitive.template import Template
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.primitive.time import WhenNode
from knowde.feature.parsing.sysnet.errors import DefSentenceConflictError
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import Duplicable

if TYPE_CHECKING:
    import networkx as nx


class IDef(BaseModel, ABC, frozen=True):
    """super定義."""

    def __repr__(self) -> str:  # noqa: D105
        return str(self)

    @abstractmethod
    def __str__(self) -> str:  # noqa: D105
        raise NotImplementedError

    @abstractmethod
    def add_edge(self, g: nx.DiGraph) -> None:
        """定義エッジ追加."""
        raise NotImplementedError


class Def(IDef, frozen=True):
    """定義."""

    term: Term
    sentence: str | DummySentence

    @classmethod
    def create(cls, sentence: str, names: list[str], alias: str | None = None) -> Self:
        """便利コンストラクタ."""
        t = Term.create(*names, alias=alias)
        return cls(term=t, sentence=sentence)

    @override
    def __str__(self) -> str:
        return f"{self.term}: {self.sentence}"

    @classmethod
    @cache
    def dummy(cls, t: Term) -> Self:
        """Create vacuous def."""
        return cls(term=t, sentence=DummySentence())

    @classmethod
    def dummy_from(cls, *names: str, alias: str | None = None) -> Self:
        """Create vacuous def."""
        t = Term.create(*names, alias=alias)
        return cls.dummy(t)

    @override
    def add_edge(self, g: nx.DiGraph) -> None:
        """定義の追加."""
        terms = list(EdgeType.DEF.pred(g, self.sentence))
        match len(terms):
            case 0:  # 新規登録
                EdgeType.DEF.add_edge(g, self.term, self.sentence)
            case _:
                msg = f"'{self}'が他の定義文と重複しています"
                raise DefSentenceConflictError(msg, terms)

    @property
    def is_dummy(self) -> bool:
        """文がダミー."""
        return isinstance(self.sentence, DummySentence)


DUMMY_SENTENCE: Final = "<<<not defined>>>"


class DummySentence(Duplicable, frozen=True):
    """Termのみの場合に擬似的に定義とみなすための空文字列."""

    n: str = DUMMY_SENTENCE


type _KNElem = str | Duplicable | Template | WhenNode  # 共通型
type KNode = Term | _KNElem
type KNArg = Def | _KNElem


META_TYPES: Final = ["AUTHOR", "PUBLISHED", "URL"]


def is_meta(v: KNode) -> bool:
    """sysnetのメタ情報 ex. 著者とか."""
    return isinstance(v, Token) and v.type in META_TYPES

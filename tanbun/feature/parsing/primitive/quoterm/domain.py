"""用語引用domain."""

import re
from collections.abc import Callable, Hashable
from typing import Final

import networkx as nx

from tanbun.feature.domain.graph.edge_type import EdgeType
from tanbun.feature.domain.types import Duplicable
from tanbun.feature.parsing.primitive.term import Term

from .errors import QuotermNotFoundError

QUOTERM_PETTERN: Final = re.compile(r"^`.*`$")


class Quoterm(Duplicable, frozen=True):
    """用語引用.

    ``で用語を囲むことで、その文の参照を置き、別ページなど他の場所で関連を作成できる
    """

    def __repr__(self) -> str:
        """Class representation."""
        return f"Quoterm({self} {str(self.uid)[:8]}..)"

    @staticmethod
    def is_quoterm(n: Hashable) -> bool:
        """引用用語 or not."""
        return bool(QUOTERM_PETTERN.match(str(n)))


type ResolveTerm = Callable[[str], Term | None]


def add_quoterm_edge(g: nx.DiGraph, resolve: ResolveTerm) -> None:
    """引用用語を1文に置換."""
    for qt in [n for n in g.nodes if isinstance(n, Quoterm)]:
        name = str(qt.n).replace("`", "")
        term = resolve(name)
        sentence = EdgeType.DEF.get_succ_or_none(g, term)
        if term is None or sentence is None:
            msg = f"'{name}'は用語として定義されていません"
            raise QuotermNotFoundError(msg)
        EdgeType.QUOTERM.add_edge(g, qt, sentence)

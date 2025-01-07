"""networkxのユーティリティ."""
from typing import Any, Hashable, Iterator

import networkx as nx

from .types import Accessor


def succ_attr(attr_name: str, value: Any) -> Accessor:  # noqa: ANN401
    """次を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterator[Hashable]:
        for _, succ, d in g.out_edges(start, data=True):
            if any(d) and d[attr_name] == value:
                _f(g, succ)
                yield succ

    return _f


def pred_attr(attr_name: str, value: Any) -> Accessor:  # noqa: ANN401
    """前を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterator[Hashable]:
        for pred, _, d in g.in_edges(start, data=True):
            if any(d) and d[attr_name] == value:
                _f(g, pred)
                yield pred

    return _f

"""networkxのユーティリティ."""

from collections.abc import Hashable, Iterable
from typing import Any

import networkx as nx

from .types import Accessor


def succ_attr(attr_name: str, value: Any) -> Accessor:
    """次を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterable[Hashable]:
        for _, succ, d in g.out_edges((start,), data=True):
            if any(d) and d[attr_name] == value:
                yield succ

    return _f


def pred_attr(attr_name: str, value: Any) -> Accessor:
    """前を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterable[Hashable]:
        for pred, _, d in g.in_edges((start,), data=True):
            if any(d) and d[attr_name] == value:
                yield pred

    return _f

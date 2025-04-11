"""nxutil types."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable

import networkx as nx

type Accessor = Callable[[nx.DiGraph, Hashable], Iterable[Hashable]]
type EdgeFilter = Callable[[Hashable, Hashable], bool]
type Edges = Iterable[tuple[Hashable, Hashable]]

"""nxutil types."""
from __future__ import annotations

from typing import Callable, Hashable, Iterable, TypeAlias

import networkx as nx

Accessor: TypeAlias = Callable[[nx.DiGraph, Hashable], Iterable[Hashable]]
EdgeFilter: TypeAlias = Callable[[Hashable, Hashable], bool]
Edges: TypeAlias = Iterable[tuple[Hashable, Hashable]]

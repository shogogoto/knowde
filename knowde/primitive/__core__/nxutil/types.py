"""nxutil types."""
from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import Callable, TypeAlias

import networkx as nx

Accessor: TypeAlias = Callable[[nx.DiGraph, Hashable], Iterable[Hashable]]
EdgeFilter: TypeAlias = Callable[[Hashable, Hashable], bool]
Edges: TypeAlias = Iterable[tuple[Hashable, Hashable]]

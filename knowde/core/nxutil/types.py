"""nxutil types."""
from typing import Callable, Hashable, Iterable, Iterator, TypeAlias

import networkx as nx

Accessor: TypeAlias = Callable[[nx.DiGraph, Hashable], Iterator[Hashable]]
EdgeFilter: TypeAlias = Callable[[Hashable, Hashable], bool]
Edges: TypeAlias = Iterable[tuple[Hashable, Hashable]]

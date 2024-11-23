from typing import Callable, Hashable, Iterator, TypeAlias

import networkx as nx

Accessor: TypeAlias = Callable[[nx.DiGraph, Hashable], Iterator[Hashable]]
EdgeFilter: TypeAlias = Callable[[Hashable, Hashable], bool]
Pairs: TypeAlias = Iterator[tuple[Hashable, Hashable]]

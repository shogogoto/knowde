"""type definitions."""

from collections.abc import Callable, Hashable, Iterable

from knowde.shared.nxutil.edge_type import EdgeType

type UpdateGetter[T] = Callable[[Iterable[T], Iterable[T]], dict[T, T]]
type UpdateGetterFactory[T] = Callable[[], UpdateGetter[T]]
type TypedEdge = tuple[Hashable, EdgeType, Hashable]

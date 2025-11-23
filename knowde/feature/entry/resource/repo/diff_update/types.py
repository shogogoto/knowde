"""type definitions."""

from collections.abc import Callable, Iterable

type UpdateGetter[T] = Callable[[Iterable[T], Iterable[T]], dict[T, T]]
type UpdateGetterFactory[T] = Callable[[], UpdateGetter[T]]
